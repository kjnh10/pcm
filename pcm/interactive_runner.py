import sys, subprocess, threading


class SubprocessThread(threading.Thread):
    def __init__(
        self,
        args,
        stdin_pipe=subprocess.PIPE,
        stdout_pipe=subprocess.PIPE,
        stderr_pipe=subprocess.PIPE,
        timeout=2,
    ):
        threading.Thread.__init__(self)
        self.p = subprocess.Popen(args, stdin=stdin_pipe, stdout=stdout_pipe, stderr=stderr_pipe, universal_newlines=True)  # universal_newlines = Trueをつけないとjudgeとthreadが入り乱れる。
        self.return_code = None
        self.error_message = None
        self.timeout = timeout

    def run(self):
        try:
            self.return_code = self.p.wait(timeout=self.timeout)
        except (SystemError, OSError):
            self.return_code = -1
            self.error_message = "SystemError, OSError"
        except subprocess.TimeoutExpired:
            self.return_code = -2
            self.error_message = "TLE"
