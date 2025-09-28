from __future__ import annotations

from io import BytesIO

from starlette.responses import StreamingResponse

from esg_tool.utils.filesystem import MIME_TYPE_DOCX


def download(filename: str, binary_data: bytes) -> StreamingResponse:
    """Stream a Word document to the client."""
    stream = BytesIO(binary_data)
    stream.seek(0)
    response = StreamingResponse(stream, media_type=MIME_TYPE_DOCX)
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
