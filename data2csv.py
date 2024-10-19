from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
import os

# Result Directory
RESULTS_CSV_DIR = "DIR_HERE"

# Function to append data to the file
def append_to_file(data):
    with open(output_file_path, 'a') as f:
        f.write(data + "\n")

# Get the flowfile from the session
flowFile = session.get()

if flowFile is not None:
    try:
        # Read the content of the flowfile
        inputStream = session.read(flowFile)
        flowfile_content = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputStream.close()

        # Append the flowfile content to the output file
        append_to_file(flowfile_content)

        # Log success
        log.info("Appended data to file: " + output_file_path)

        # Transfer the flowfile to the success relationship
        session.transfer(flowFile, REL_SUCCESS)

    except Exception as e:
        # If there's an error transfer the flowfile to failure relationship
        log.error("Failed to append to file: " + str(e))
        session.transfer(flowFile, REL_FAILURE)