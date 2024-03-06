import fileinput
import shutil

class smartReplace():
    def __init__(self, tex_file):
        self.filename = tex_file
        self.new_file = self.filename.replace('.tex', '_modified.tex')

        shutil.copy(self.filename, self.new_file)
        
        self.pattern = [f"\\multicolumn{{1}}{{p{{\\tbtextsz}}|}}{{{d}}}" for d in range(10)]
        self.origin_text = "tbtextsz"
        self.replace_text = "---------"

    def advReplace(self):
        self.new_lines = []
        # Iterate through the file and replace matching lines
        with open(self.new_file, 'r') as file:
            for line in file.readlines():
                # check for extras
                if self.skipLine(line):
                    continue

                if any(pattern_item in line for pattern_item in self.pattern):
                    new_line = line.replace(self.origin_text, self.replace_text)
                    self.new_lines.append(new_line)
                else:
                    self.new_lines.append(line)

        # Write the modified lines back to the file
        with open(self.new_file, 'w') as file:
            file.writelines(self.new_lines)
    
    def replace(self):
        self.new_lines = []
        # Iterate through the file and replace matching lines
        with open(self.new_file, 'r') as file:
            for line in file.readlines():
                # check for extras
                if self.skipLine(line):
                    continue

                new_line = line.replace(self.origin_text, self.replace_text)
                self.new_lines.append(new_line)

        # Write the modified lines back to the file
        with open(self.new_file, 'w') as file:
            file.writelines(self.new_lines)

    def idc(self):
        manual_adds = [r"Severity \\ (1-10)",r"Occurrence \\ (1-10)",r"Detection \\ (1-10)"]
        # manual adds
        self.new_lines = []
        # Iterate through the file and replace matching lines
        with open(self.new_file, 'r') as file:
            for line in file.readlines():
                # check for extras
                if self.skipLine(line):
                    continue

                if r"\cellcolor" in line and r"\ \hline" in line and r"multirow" not in line:
                    print(line)
                    col = r"\multicolumn{1}{p{\tbnumsz}|}{"
                    c = r"}"
                    new_line = f"{line[0:4]}{col}{line[4:-11]}{c} \\\\ \hline\n"
                    print(new_line)
                    self.new_lines.append(new_line)
                elif any(pattern_item in line for pattern_item in manual_adds):
                    new_line = line.replace("tbtextsz", "tbnumsz")
                    self.new_lines.append(new_line)
                else:
                    self.new_lines.append(line)

        # Write the modified lines back to the file
        with open(self.new_file, 'w') as file:
            file.writelines(self.new_lines)
        
        # manual adds

        # # do the middle column too
        # new_lines = []
        # # Iterate through the file and replace matching lines
        # with open(self.new_file, 'r') as file:
        #     for line in file.readlines():
        #         if r"\cellcolor" in line:
        #             new_line = line.replace("tbtextsz", "tbnumsz")
        #             new_lines.append(new_line)
        #         else:
        #             new_lines.append(line)

        # # Write the modified lines back to the file
        # with open(self.new_file, 'w') as file:
        #     file.writelines(new_lines)

    def skipLine(self, _line):
        _ignore = ["Failure Mode and Effects Analysis (FMEA) for system", "HARDWARE", "SOFTWARE"]
        if any(ignore_item in _line for ignore_item in _ignore):
            self.new_lines.append(_line)
            return True
        else:
            return False

    
    def betterWay(self):
        self.new_lines = []
        cols_to_change = [4,5,6,7,9,10,11,12]

        xy = []
        # Iterate through the file and replace matching lines
        with open(self.new_file, 'r') as file:
            for idx, line in enumerate(file.readlines()):
                # print(line.split("&"))
                xy.append(line.split("&"))
                for col in cols_to_change:
                    if idx == 11:
                        xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbnumsz")
                    if idx >= 14 and idx <= 33:
                        xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbnumsz")
                    if idx >= 36 and idx <= 41:
                        xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbnumsz")
                
                # change this to be modular
                col = 8
                if idx == 11:
                    xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbtextszz")
                if idx >= 14 and idx <= 33:
                    xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbtextszz")
                if idx >= 36 and idx <= 41:
                    xy[idx][col] = xy[idx][col].replace("tbtextsz", "tbtextszz")

                "&".join(xy[idx])
                print("&".join(xy[idx]))
                print()
                self.new_lines.append("&".join(xy[idx]))
        print(xy[14][0])
        print(xy[33][0])
        print(xy[36][0])
        print(xy[41][0])


                # new_line = line.replace(self.origin_text, self.replace_text)
                # self.new_lines.append(new_line)

        # Write the modified lines back to the file
        with open(self.new_file, 'w') as file:
            file.writelines(self.new_lines)

    def find_cols(self):
        with open(self.new_file, 'r') as file:
            for idx, line in enumerate(file.readlines()):
                # print(line.split("&")[0])
                # xy.append(line.split("&"))
                if "\\multicolumn{1}" in line.split("&")[0]:
                    col_num = len(line.split("&"))
                    print(f"{col_num} Columnds detected")
                    return col_num


    
    def modularColChange(self, col, txt, row_range = None):
        self.new_lines = []

        xy = []
        # Iterate through the file and replace matching lines
        with open(self.new_file, 'r') as file:
            for idx, line in enumerate(file.readlines()):
                # print(line.split("&"))
                xy.append(line.split("&"))
                if "\\multicolumn{1}" in xy[idx][0] and row_range is None:
                    xy[idx][col] = xy[idx][col].replace(txt[0], txt[1])
                    self.new_lines.append("&".join(xy[idx]))
                elif row_range is not None and idx >= row_range[0] and idx <= row_range[1]:
                    xy[idx][col] = xy[idx][col].replace(txt[0], txt[1])
                    self.new_lines.append("&".join(xy[idx]))
                else:
                    self.new_lines.append(line)

                # if idx >= row_range[0] and idx <= row_range[1]:
                #     print(len(xy[idx]))
                #     print(xy[idx])
                #     print()
                #     xy[idx][col] = xy[idx][col].replace(txt[0], txt[1])
                #     self.new_lines.append("&".join(xy[idx]))
                # else:
                #     self.new_lines.append(line)
        # print("-------- Rows changed")
        # print(xy[row_range[0]][col])
        # print(xy[row_range[1]][col])

        # print()
        # print()
        # print()
        # print()

        # Write the modified lines back to the file
        with open(self.new_file, 'w') as file:
            file.writelines(self.new_lines)
        

if __name__ == '__main__':
    r = smartReplace("fmea.tex")

    alph="a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z".split(", ")

    cmds = []
    # replace the final columng too
    r.modularColChange(0, ["c|",f"p{{\\colz}}|"], [6,6])
    cmdstr = f"\\newcommand{{\\colz}}{{5cm}}"
    cmds.append(cmdstr)

    for i in range(r.find_cols()):
        r.modularColChange(i, ["c|",f"p{{\\col{alph[i]}}}|"])
        r.modularColChange(i, ["|c|",f"|p{{\\col{alph[i]}}}|"])

        cmdstr = f"\\newcommand{{\\col{alph[i]}}}{{5cm}}"
        cmds.append(cmdstr)
    
    for i in cmds:
        print(i)


    # # simple replace
    # r.origin_text = "c|"
    # r.replace_text = "p{\\tbtextsz}|"
    # r.replace()

    # r.origin_text = "|c|"
    # r.replace_text = "|p{\\tbtextsz}|"
    # r.replace()

    # r.betterWay()

    



    # # advanced replace
    # r.pattern = [f"\\multicolumn{{1}}{{p{{\\tbtextsz}}|}}{{{d}}}" for d in range(10)]
    # r.origin_text = "tbtextsz"
    # r.replace_text = "tbnumsz"
    # r.advReplace()

    # # inilne repalce
    # r.pattern = [f"\\ \hline"]
    # r.idc()
