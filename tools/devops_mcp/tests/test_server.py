import pytest
from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents
from pathlib import Path
import os
import sys

from devops_mcp.server import mcp
from devops_mcp.catalog import PROJECT_DIR


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_tools_search_and_return_practical():
    async with Client(mcp, raise_exceptions=True) as client:
        tools = await client.list_tools()
        names = {tool.name for tool in tools.tools}
        assert {"list_phases", "search_practicals", "get_practical"} <= names

        result = await client.call_tool("search_practicals", {"query": "persistent pvc"})
        assert not result.is_error
        assert any(
            item["slug"] == "kubernetes-storage-pvc"
            for item in result.structured_content["result"]
        )

        practical = await client.call_tool(
            "get_practical", {"slug": "docker-production-image", "include_answer": True}
        )
        assert not practical.is_error
        assert "read-only root filesystem" in practical.structured_content["guide"]
        assert practical.structured_content["answer"] is None


@pytest.mark.anyio
async def test_resources_only_read_catalogued_guides():
    async with Client(mcp, raise_exceptions=True) as client:
        assert "Read-only DevOps learning companion" in client.instructions
        listed = await client.list_resources()
        assert any(str(resource.uri) == "devops://catalog" for resource in listed.resources)
        assert any(str(resource.uri) == "devops://server-guide" for resource in listed.resources)

        guide_contents = await client.read_resource("devops://server-guide")
        guide_text = next(
            item.text for item in guide_contents.contents if isinstance(item, TextResourceContents)
        )
        assert "Safety contract" in guide_text

        contents = await client.read_resource("devops://practicals/linux-host-incident/guide")
        text = next(item.text for item in contents.contents if isinstance(item, TextResourceContents))
        assert "synthetic" in text.lower()

        missing = await client.read_resource("devops://practicals/unknown-practical/guide")
        missing_text = next(item.text for item in missing.contents if isinstance(item, TextResourceContents))
        assert "Unknown practical slug" in missing_text


@pytest.mark.anyio
async def test_prompts_include_safety_boundary():
    async with Client(mcp, raise_exceptions=True) as client:
        prompts = await client.list_prompts()
        assert {"incident_triage", "production_change_review", "practical_study_plan"} <= {
            prompt.name for prompt in prompts.prompts
        }
        result = await client.get_prompt(
            "incident_triage",
            {"practical_slug": "linux-host-incident", "symptoms": "5xx increased"},
        )
        prompt_text = "\n".join(
            message.content.text
            for message in result.messages
            if isinstance(message.content, TextContent)
        )
        assert "Do not run commands" in prompt_text
        assert "5xx increased" in prompt_text


@pytest.mark.anyio
async def test_stdio_server_lists_tools_from_subprocess():
    project_python = Path(sys.executable)
    params = StdioServerParameters(
        command=str(project_python),
        args=["-m", "devops_mcp.server"],
        cwd=PROJECT_DIR,
        env={"PYTHONPATH": os.environ.get("PYTHONPATH", "")},
    )
    async with Client(params) as client:
        result = await client.list_tools()
        assert {"list_phases", "search_practicals", "get_practical"} <= {
            tool.name for tool in result.tools
        }