import sys
import os
import traceback
import datetime

class DebugLogger:
    def __init__(self):
        self.log_file = os.path.join(os.getcwd(), "debug_log.txt")
        # Clear previous log
        with open(self.log_file, "w") as f:
            f.write(f"Session started at {datetime.datetime.now()}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"CWD: {os.getcwd()}\n")
            f.write("-" * 50 + "\n")

    def write(self, message):
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            with open(self.log_file, "a") as f:
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass

    def flush(self):
        pass

def setup_logging():
    # Only setup if frozen or explicitly requested
    if getattr(sys, 'frozen', False) or os.environ.get('DEBUG_LOGGING'):
        logger = DebugLogger()
        sys.stdout = logger
        sys.stderr = logger
        
        # Hook excepthook
        def exception_hook(exctype, value, tb):
            logger.write("Uncaught Exception:")
            logger.write("".join(traceback.format_exception(exctype, value, tb)))
            sys.__excepthook__(exctype, value, tb)
            
        sys.excepthook = exception_hook
        print("Debug logging enabled.")
