import os
from tkinter import Tk
from tkinter import Menu
from tkinter import ttk
import argparse

import pyperclip
from tabler import Tabler
import stclocal

from . skuconvert import LinnSKUConverter


class ConvertForm():
    def __init__(self, app, parent, from_label, to_label, channels,
                 convert_function):
        self.app = app
        self.parent = parent
        self.convert_function = convert_function

        self.channel_label = ttk.Label(
            parent, text="Channel")
        self.channel_label.grid(row=0, column=0, sticky='EW')

        self.channel_selector = ttk.Combobox(
            parent, values=channels)
        self.channel_selector.grid(row=0, column=1, columnspan=2, sticky='EW')

        self.input_sku_label = ttk.Label(
            parent, text=from_label)
        self.input_sku_label.grid(row=1, column=0, sticky='W')

        self.input_sku_entry = ttk.Entry(parent)
        self.input_sku_entry.grid(row=1, column=1, sticky='EW')
        self.input_sku_entry.bind("<Return>", self.convert)
        self.input_sku_entry.bind('<Button-3>', self.right_clicker, add='')

        self.convert_button = ttk.Button(
            parent, text="Convert", command=lambda: self.convert(None))
        self.convert_button.grid(row=1, column=3)

        self.output_sku_label = ttk.Label(
            parent, text=to_label)
        self.output_sku_label.grid(row=2, column=0, sticky='EW')

        self.output_sku_entry = ttk.Entry(parent)
        self.output_sku_entry.grid(row=2, column=1)
        self.output_sku_entry.bind('<Button-3>', self.right_clicker, add='')

        self.copy_button = ttk.Button(
            parent, text="Copy", command=lambda: self.app.to_clipboard(
                self.output_sku_entry.get()))
        self.copy_button.grid(row=2, column=3)

    def right_clicker(self, e):
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-a>')
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-a>')
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.delete(0, "end")
            e.widget.event_generate('<Control-v>')

        e.widget.focus()
        nclst = [
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e))]
        rmenu = Menu(None, tearoff=0, takefocus=0)
        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)
        rmenu.tk_popup(e.x_root+40, e.y_root+10, entry="0")

    def convert(self, event):
        self.output_sku_entry.delete(0, 'end')
        input_sku = self.input_sku_entry.get().strip()
        print(input_sku)
        channel_name = self.channel_selector.get()
        channel = self.app.channel_lookup[channel_name]
        print(channel)
        output_skus = self.convert_function(input_sku, channel)
        if len(output_skus) > 0:
            output = output_skus[0]
            self.app.to_clipboard(output)
        else:
            output = "ERROR"
            self.app.to_clipboard('')
        self.output_sku_entry.insert(0, string=output)


class SKUConverterApp():
    def __init__(self, converter):
        self.root = Tk()
        self.root.title('SKU Converter')
        self.notebook = ttk.Notebook(self.root)
        self.channel_to_linn_page = ttk.Frame(self.notebook)
        self.linn_to_channel_page = ttk.Frame(self.notebook)
        self.notebook.add(
            self.channel_to_linn_page, text="Channel to Linnworks SKU")
        self.notebook.add(
            self.linn_to_channel_page, text="Linnworks to Channel SKU")
        self.notebook.grid(row=0, column=0, sticky='EW')
        self.style = ttk.Style()
        self.converter = converter
        self.channel_lookup = self.get_channel_lookup()
        self.channels = list(self.channel_lookup.keys())
        self.channels.sort()
        self.linn_to_channel = ConvertForm(
            self, self.linn_to_channel_page, "Linnworks SKU", "Channel SKU",
            self.channels, self.converter.get_channel_skus)
        self.channel_to_linn = ConvertForm(
            self, self.channel_to_linn_page, "Channel SKU", "Linnworks SKU",
            self.channels, self.converter.get_linn_skus)

    def to_clipboard(self, text):
        pyperclip.copy(text)

    def get_channel_lookup(self):
        return {
            'eBay': 'EBAY0',
            'Amazon UK': 'Stc Stores',
            'Amazon FR': 'STC Stores France',
            'Amazon DE': 'STC Stores Germany',
            'Amazon ES': 'STC Stores Spain',
            'Amazon USA': 'STC Stores USA',
            'Shopify': 'stcstores.co.uk (shopify)',
        }


def main():
    def get_recent_linking_file():
        backups = [f for f in os.scandir(stclocal.BACKUP_DIR) if f.is_dir()]
        backups.sort(key=lambda x: x.path)
        directory = backups[-3]
        date = directory.name
        filename = '_'.join([date, stclocal.LINKING_FILE_NAME])
        return os.path.join(directory.path, filename)

    parser = argparse.ArgumentParser()
    parser.add_argument('linking_file', default='', type=str, nargs='?')
    parser.add_argument('-r', '--recent', action='store_true', dest='recent')
    parser.add_argument('--no-recent', action='store_false', dest='recent')
    parser.set_defaults(recent=False)
    args = parser.parse_args()
    if len(args.linking_file) > 0:
        linking_file_path = args.linking_file
        print('Loading from {}'.format(linking_file_path))
        converter = LinnSKUConverter(Tabler(linking_file_path))
    elif args.recent is True:
        linking_file_path = get_recent_linking_file()
        print('Loading from {}'.format(linking_file_path))
        converter = LinnSKUConverter(Tabler(linking_file_path))
    else:
        print('Loading from Linnworks.net')
        converter = LinnSKUConverter()
    app = SKUConverterApp(converter)
    app.root.mainloop()


if __name__ == "__main__":
    main()
