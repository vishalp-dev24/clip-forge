import aiofiles
import shutil
from pathlib import Path

async def save_upload_file(upload_file, destination: str):
    """
    Asynchronously saves an uploaded file to a specified destination.

    This function takes an uploaded file object and a destination path. It creates the
    necessary directory structure if it doesn't exist. The file is then read in chunks
    and written to the destination file asynchronously. This is efficient for handling
    large files as it doesn't block the server's main thread.

    Args:
        upload_file: The file object to be saved. This is typically obtained from a
                     web framework's request object. It should have an async `read` method.
        destination (str): The path (including filename) where the file should be saved.

    Returns:
        str: The string representation of the destination path where the file was saved.
    """
    dest_path = Path(destination)
    # Create parent directories if they don't exist
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    # Open the destination file in binary write mode
    async with aiofiles.open(dest_path, "wb") as out_file:
        while True:
            # Read the file in 1MB chunks
            chunk = await upload_file.read(1024*1024)
            if not chunk:
                break
            # Write the chunk to the destination file
            await out_file.write(chunk)
    # Ensure the uploaded file is closed
    await upload_file.close()
    return str(dest_path)