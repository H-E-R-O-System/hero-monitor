import pandas as pd

class xl2tex():
    def __init__(self):
        xl_file = 'GSPR.xlsx'

        all_sheets_dict = pd.read_excel(xl_file, sheet_name=None)

        for sheet_name, sheet_data in all_sheets_dict.items():
            print(f"Sheet Name: {sheet_name}")
            print(sheet_data.head())
            self.sheet2tex(sheet_data, sheet_name)
            print("\n")
    
    def sheet2tex(self, sheet, sh_name):
        print("converted")
        latex_table = self.dataframe_to_latex(sheet)

        with open(f"tables/{sh_name}.tex", 'w') as latex_file:
            latex_file.write(latex_table)
    
    def column_format(self, df, decimal_format='{:,.0f}'):
        df_formatted = df.copy()
        for col in df.select_dtypes(include='float64').columns:
            df_formatted[col] = df[col].apply(lambda x: decimal_format.format(x))
        return df_formatted
    
    def dataframe_to_latex(self, df, caption='', label=''):
        # reound to how many decimal places
        df.round(decimals=0)

        latex_code = "\\documentclass[12pt]{article}\n"

        # packages
        latex_code += "\\usepackage{graphicx}\n"
        latex_code += "\\usepackage{float}\n\n"

        # document
        latex_code += "\\begin{document}\n\n"
        latex_code += "\\begin{table}[H]\n"
        latex_code += "\\centering\n"
        latex_code += "\\resizebox{\\columnwidth}{!}{\n"
        
        # Begin tabular environment with column headers
        latex_code += "\\begin{tabular}{"
        # latex_code += "|".join(["c"] * len(df.columns))
        latex_code += f"*{{{len(df.columns)}}}{{|c}}"
        latex_code += "|}\n"
        
        # Add column names as the first row
        latex_code += "\\hline\n"
        latex_code += " & ".join(map(str, df.columns)) + " \\\\\n"
        latex_code += "\\hline\n"
        
        # # Add data rows
        # for index, row in df.iterrows():
        #     latex_code += " & ".join(map(str, row)) + " \\\\ \\hline\n"
        decimal_format='{:,.0f}'
        # Add data rows
        df_formatted = self.column_format(df, decimal_format)
        for index, row in df_formatted.iterrows():
            latex_code += " & ".join(map(str, row)) + " \\\\ \\hline\n"
        
        # End tabular environment
        latex_code += "\\end{tabular}\n}\n"
        
        # Add caption and label
        if caption:
            latex_code += f"\\caption{{{caption}}}\n"
        if label:
            latex_code += f"\\label{{{label}}}\n"
        
        # End table environment
        latex_code += "\\end{table}\n\n"
        latex_code += "\\end{document}"
        
        return latex_code



if __name__ == "__main__":
    x2t = xl2tex()
