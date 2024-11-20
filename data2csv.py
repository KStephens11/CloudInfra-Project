from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
import os

# Result Directory
OUTPUT_CSV_DIR = "CSV_DIR_HERE"

# Get the flowfile from the session
flowFile = session.get()

if flowFile is not None:
    try:
        # Read the content of the flowfile
        inputStream = session.read(flowFile)
        flowfile_data = IOUtils.toString(inputStream, StandardCharsets.UTF_8)
        inputStream.close()
        
        # Append flowfile data to the file
        with open(OUTPUT_CSV_DIR, 'a') as f:
            f.write(flowfile_data + "\n")

        # Log success
        log.info("Successfully appended data to file")

        # Transfer the flowfile to the success relationship
        session.transfer(flowFile, REL_SUCCESS)

    except Exception as e:
        # If there's an error transfer the flowfile to failure relationship
        log.error("Failed to append to file, error:", str(e))
        session.transfer(flowFile, REL_FAILURE)