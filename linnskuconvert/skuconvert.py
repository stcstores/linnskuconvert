import copy

from tabler import Tabler as Table

import stclocal


class LinnSKUConverter():
    """ Creates a lookup table to convert Amazon SKUs to Linnworks
    SKUs. Used to find the Linnworks SKU to which a European
    Amazon listing created by Webinterpret should be linked
    as this will have the same SKU as the UK listing from
    which it was created.
    """

    def __init__(self, linking_table=None):
        if linking_table is not None:
            if isinstance(linking_table, Table):
                self.linking_table = linking_table
            elif isinstance(linking_table, str):
                self.linking_table = Table(linking_table)
            else:
                raise TypeError("linking_table must be str or tabler.Tabler")
        else:
            self.linking_table = self.get_linking_table()
        self.channels = list(set(self.linking_table.get_column('Sub Source')))
        self.SKUs = self.get_sku_lookup()
        self.channel_lookup = self.get_channel_lookup()

    def get_sku_lookup(self):
        SKUs = {}
        blank_sku_data = {channel: [] for channel in self.channels}
        for row in self.linking_table:
            linn_sku = row['StockSKU']
            if linn_sku not in SKUs:
                SKUs[linn_sku] = copy.deepcopy(blank_sku_data)
            SKUs[linn_sku][row['Sub Source']].append(row['ChannelSKU'])
        return SKUs

    def get_linking_table(self):
        """ Aquire current linking information from linnworks API. """
        export = stclocal.PyLinnworks.Export()
        return export.get_linking_table()

    def get_channel_skus(self, linn_sku, channel):
        """ Return Channel SKUs for channel linked to linn_sku. """
        sub_source = self.channel_lookup[channel.lower()]
        return self.SKUs[linn_sku][sub_source]

    def get_linn_skus(self, channel_sku, channel=None):
        """ Return Linnworks SKU linked to channel_sku. """
        sub_source = None
        if channel is not None:
            sub_source = self.channel_lookup[channel.lower()]
        linn_skus = []
        for linn_sku in self.SKUs:
            if sub_source is not None:
                if channel_sku in self.SKUs[linn_sku][sub_source]:
                    linn_skus.append(linn_sku)
            else:
                for channel in self.SKUs[linn_sku]:
                    if channel_sku in self.SKUs[linn_sku][channel]:
                        linn_skus.append(linn_sku)
        return linn_skus

    def is_linked(self, linn_sku, channel):
        sub_source = self.channel_lookup[channel.lower()]
        try:
            item_linking = self.SKUs[linn_sku]
        except KeyError:
            return False
        return len(item_linking[sub_source]) != 0

    def get_channel_lookup(self):
        """ Creates lookup to allow various channel names. """
        lookup = {
            sub_source.lower(): sub_source for sub_source in self.channels}
        if 'EBAY0' in self.channels:
            lookup['ebay'] = 'EBAY0'
        if 'Stc Stores' in self.channels:
            lookup['amazon'] = 'Stc Stores'
            lookup['amazonuk'] = 'Stc Stores'
            lookup['amazon uk'] = 'Stc Stores'
            lookup['amazon.co.uk'] = 'Stc Stores'
        if 'STC Stores France' in self.channels:
            lookup['STC Stores France'] = 'STC Stores France'
            lookup['amazon france'] = 'STC Stores France'
            lookup['amazonfr'] = 'STC Stores France'
            lookup['amazon fr'] = 'STC Stores France'
            lookup['amazon.fr'] = 'STC Stores France'
        if 'STC Stores Germany' in self.channels:
            lookup['amazon germany'] = 'Stc Stores Germany'
            lookup['amazonde'] = 'Stc Stores Germany'
            lookup['amazon de'] = 'Stc Stores Germany'
            lookup['amazon.de'] = 'Stc Stores Germany'
        if 'STC Stores Spain' in self.channels:
            lookup['amazon spain'] = 'Stc Stores Spain'
            lookup['amazones'] = 'Stc Stores Spain'
            lookup['amazon es'] = 'Stc Stores Spain'
            lookup['amazon.es'] = 'Stc Stores Spain'
        if 'STC Stores Italy' in self.channels:
            lookup['amazon italy'] = 'Stc Stores Italy'
            lookup['amazonit'] = 'Stc Stores Italy'
            lookup['amazon it'] = 'Stc Stores Italy'
            lookup['amazon.it'] = 'Stc Stores Italy'
        if 'Stc Stores USA' in self.channels:
            lookup['amazon us'] = 'Stc Stores USA'
            lookup['amazonus'] = 'Stc Stores USA'
            lookup['amazon us'] = 'Stc Stores USA'
            lookup['amazon.com'] = 'Stc Stores USA'
            lookup['amazon usa'] = 'Stc Stores USA'
            lookup['amazonusa'] = 'Stc Stores USA'
            lookup['amazon america'] = 'Stc Stores USA'
            lookup['amazonamerica'] = 'Stc Stores USA'
            lookup['amazon america'] = 'Stc Stores USA'
        if 'STC Stores Canada' in self.channels:
            lookup['amazon canada'] = 'Stc Stores Canada'
            lookup['amazonca'] = 'Stc Stores Canada'
            lookup['amazon ca'] = 'Stc Stores Canada'
            lookup['amazon.ca'] = 'Stc Stores Canada'
        if 'STC Stores Mexico' in self.channels:
            lookup['amazon mexico'] = 'Stc Stores Mexico'
            lookup['amazonmx'] = 'Stc Stores Mexico'
            lookup['amazon mx'] = 'Stc Stores Mexico'
            lookup['amazon.mx'] = 'Stc Stores Mexico'
            lookup['amazon.com.mx'] = 'Stc Stores Mexico'
        if 'stcstores.co.uk (shopify)' in self.channels:
            lookup['shopify'] = 'stcstores.co.uk (shopify)'
            lookup['stcstores.co.uk'] = 'stcstores.co.uk (shopify)'
            lookup['stcstores.com'] = 'stcstores.co.uk (shopify)'
        return lookup
