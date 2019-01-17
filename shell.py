import clips as _clips
import sys as _sys
import string as _string


class Shell(object):
    """
    An interactive CLIPS shell
    """

    def __init__(self):
        self.__ps1 = "CLIPS[%(cmdno)s/%(lineno)s]> "
        self.__ps2 = "CLIPS[%(cmdno)s/%(lineno)s]: "
        self.__cmdno = 1
        self.__lineno = 1

    @staticmethod
    def cmd_complete(cms):
        """
        Check if CLIPS command is complete
        """

        def eat_ws(i):
            """
            Eat up whitespace
            """

            while i < len(cms.strip()) and cms.strip()[i] in _string.whitespace:
                i += 1
            return i

        def eat_string(i):
            """
            Eat up strings
            """

            if cms.strip()[i] != '"' or i >= len(cms.strip()):
                return i
            i += 1
            while i < len(cms.strip()):
                if cms.strip()[i] == '"':
                    return i + 1
                else:
                    if cms.strip()[i] == '\\':
                        i += 1
                    i += 1
            if i > len(cms.strip()):
                raise ValueError("non-terminated string")
            return i

        def eat_comment(i):
            """
            Eat up comments
            """

            if cms.strip()[i] != ';' or i >= len(cms.strip()):
                return i
            while i < len(cms.strip()) and cms.strip()[i] not in '\n\r':
                i += 1
            return i + 1

        if len(cms.strip()) == 0:
            return False
        depth = 0
        i = 0
        while i < len(cms.strip()):
            c = cms.strip()[i]
            if c in '\n\r' and depth == 0:
                return True
            elif c == '"':
                i = eat_string(i)
            elif c == ';':
                i = eat_comment(i)
            elif c == '(':
                depth += 1
                i += 1
            elif c == ')':
                depth -= 1
                i += 1
            elif c in _string.whitespace:
                i = eat_ws(i)
            else:
                i += 1
            if depth < 0:
                raise ValueError("invalid command")
        if depth == 0:
            return True
        else:
            return False

    def run(self):
        """
        Start or resume an interactive CLIPS shell
        """

        exit_flag = False
        while not exit_flag:
            self.__lineno = 1
            s = ""
            dic = {'cmdno': self.__cmdno, 'lineno': self.__lineno}
            prompt = self.__ps1 % dic
            try:
                while not self.cmd_complete(s):
                    if s:
                        s += " "
                    s += raw_input(prompt).strip()
                    self.__lineno += 1
                    dic = {'cmdno': self.__cmdno, 'lineno': self.__lineno}
                    prompt = self.__ps2 % dic
            except ValueError as e:
                _sys.stderr.write("[SHELL] %s\n" % str(e))
            except EOFError:
                _clips.ErrorStream.Read()
                exit_flag = True
            try:
                if not exit_flag:
                    _clips.SendCommand(s, True)
            except _clips.ClipsError as e:
                _sys.stderr.write("[PYCLIPS] %s\n" % str(e))
            self.__cmdno += 1
            r0 = _clips.StdoutStream.Read()
            r1 = _clips.DisplayStream.Read()
            tx = _clips.TraceStream.Read()
            r = ""
            if r0:
                r += r0
            if r1:
                r += r1
            t = _clips.ErrorStream.Read()
            if r:
                r = "%s\n" % r.rstrip()
            if t:
                t = "%s\n" % t.rstrip()
            if tx:
                t = "%s\n" % tx.rstrip() + t
            if t:
                _sys.stderr.write(t)
            if r:
                _sys.stdout.write(r)


if __name__ == "__main__":
    Shell().run()
