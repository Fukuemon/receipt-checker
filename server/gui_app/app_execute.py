import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import customtkinter
import os
from function import receipt_check

FONT_TYPE = "meiryo"
PRIMARY = "blue"
BACK_COLOR = "dark"
FONT_COLOR = "white"
FORM_SIZE = "1000x600"


class ReadCsvFrame(customtkinter.CTkFrame):
    def __init__(self, master, header_name, placeholder_text, **kwargs):
        super().__init__(master, **kwargs)
        self.fonts = (FONT_TYPE, 15)
        self.header_name = header_name
        self.file_path = None

        self.grid_columnconfigure(0, weight=1)
        self.label = customtkinter.CTkLabel(self, text=self.header_name, font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")

        self.textbox = customtkinter.CTkEntry(self, placeholder_text=placeholder_text, width=120, font=self.fonts)
        self.textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        self.button_select = customtkinter.CTkButton(self, command=self.button_select_callback, text="ファイル選択",
                                                     fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), font=self.fonts)
        self.button_select.grid(row=1, column=1, padx=10, pady=(0, 10))

    def button_select_callback(self):
        file_name = self.file_read()
        if file_name or file_name == "":  # ファイル選択がキャンセルされた場合、file_name は空文字列となる
            if file_name:
                self.file_path = file_name  # 新しいファイルパスを設定
                self.textbox.delete(0, tk.END)
                self.textbox.insert(0, file_name)
            else:
                # キャンセルされた場合、テキストボックスは元のパスを表示
                self.textbox.delete(0, tk.END)
                if self.file_path:
                    self.textbox.insert(0, self.file_path)

    @staticmethod
    def file_read():
        current_dir = os.path.abspath(os.path.dirname(__file__))
        file_path = filedialog.askopenfilename(filetypes=[("CSVファイル", "*.csv")], initialdir=current_dir)
        return file_path


class ReadReceiptCsvFrame(ReadCsvFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, header_name="レセプトファイル選択", placeholder_text="レセプトのCSVファイルを読み込む", **kwargs)

class ReadCalendarIdsCsvFrame(ReadCsvFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, header_name="カレンダーファイル選択", placeholder_text="カレンダーIDのCSVファイルを読み込む", **kwargs)

class DataDisplayFrame(customtkinter.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fonts = (FONT_TYPE, 15)
        self.result_df = None

        self.setup_form()

    def setup_form(self):

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(self, text="照合結果", font=(FONT_TYPE, 11))
        self.label.grid(row=0, column=0, padx=20, sticky="w")
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky="nsew")

        self.scroll_y = customtkinter.CTkScrollbar(self, orientation="vertical", command=self.tree.yview)
        self.scroll_y.grid(row=1, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_x = customtkinter.CTkScrollbar(self, orientation="horizontal", command=self.tree.xview)
        self.scroll_x.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.tree.configure(xscrollcommand=self.scroll_x.set)

        self.button_download = customtkinter.CTkButton(master=self, command=self.download_csv,
                                                       text="CSVとしてダウンロード",
                                                       font=self.fonts)
        self.button_download.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def display_dataframe(self, df):
        for column in self.tree.get_children():
            self.tree.delete(column)

        self.tree["columns"] = list(df.columns)

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        for index, row in df.iterrows():
            self.tree.insert("", tk.END, values=list(row))

        self.result_df = df

    def download_csv(self):
        if self.result_df is None:
            messagebox.showwarning("警告", "表示するデータがありません")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSVファイル", "*.csv")])
        if save_path:
            self.result_df.to_csv(save_path, index=False)
            messagebox.showinfo("情報", f"CSVファイルが保存されました: {save_path}")


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.fonts = (FONT_TYPE, 15)
        self.geometry(FORM_SIZE)
        self.title("CSV input")
        self.setup_form()

    def setup_form(self):
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.receipt_frame = ReadReceiptCsvFrame(self)
        self.receipt_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.calendar_frame = ReadCalendarIdsCsvFrame(self)
        self.calendar_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="ew")

        self.button_execute = customtkinter.CTkButton(self, text="実行", command=self.button_execute_callback, font=self.fonts)
        self.button_execute.grid(row=2, column=0, padx=20, pady=(10, 20))

        self.data_display_frame = DataDisplayFrame(self)
        self.data_display_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")

    def button_execute_callback(self):
        receipt_file = self.receipt_frame.file_path
        calendar_file = self.calendar_frame.file_path
        if not receipt_file or not calendar_file:
            messagebox.showwarning("警告", "レセプトファイルおよびカレンダーファイルを選択してください")
            return
        try:
            result_df = receipt_check(receipt_file, calendar_file)
            self.data_display_frame.display_dataframe(result_df)
        except Exception as e:
            messagebox.showerror("エラー", f"処理中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    app = App()
    app.mainloop()

