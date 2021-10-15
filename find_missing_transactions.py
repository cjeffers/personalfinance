#! /usr/bin/env python3

import datetime
import glob
import pandas as pd
import pprint
import pdb
import sys


DATE_INPUT_PATTERN = '%m/%d/%Y'
DATE_OUTPUT_PATTERN = '%Y-%m-%d'


def main(folder):
    chase_transactions = load_chase_transactions(folder)
    quicken_transactions = load_quicken_transactions(folder)

    for ct in chase_transactions:
        if ct['date'] not in quicken_transactions:
            pprint.pprint(ct)
        else:
            date_transactions = quicken_transactions[ct['date']]
            if ct['amount'] not in date_transactions:
                pprint.pprint(ct)
            else:
                amount_transactions = date_transactions[ct['amount']]
                if all([t['seen'] for t in amount_transactions]):
                    pprint.pprint(ct)
                else:
                    next_trans = next(t for t in amount_transactions if not t['seen'])
                    next_trans['seen'] = True



def load_chase_transactions(folder):
    chase_file = glob.glob(f"./{folder}/*.CSV")[0]
    df = pd.read_csv(chase_file)
    print(f"chase: {len(df)} trans, {sum(df['Amount'])} total")
    return [
        {
            'date': get_date(r['Post Date']),
            'description': r['Description'],
            'amount': get_money(r['Amount'])
        } for i, r in df.iterrows()
    ]


def get_date(date_str):
    try:
        if pd.isna(date_str):
            return None
        date = datetime.datetime.strptime(date_str, DATE_INPUT_PATTERN)
        return date.strftime(DATE_OUTPUT_PATTERN)
    except ValueError:
        pdb.set_trace()


def get_money(money_str):
    if type(money_str) is str:
        money_str = money_str.replace(',', '')
    return str(float(money_str))


def load_quicken_transactions(folder):
    quicken_file = glob.glob(f"./{folder}/*.TXT")[0]
    df = pd.read_csv(quicken_file, sep='\t')
    transactions = [
        {
            'date': get_date(r['Date']),
            'description': r['Description'],
            'amount': get_money(r['Amount']),
            'seen': False
        } for i, r in df.iterrows()
    ]
    trans_sum = sum([float(t['amount']) for t in transactions])
    print(f"quicken: {len(df)} trans, {trans_sum} total")
    print('+', sum([float(t['amount']) for t in transactions if float(t['amount']) > 0]))
    print('-', sum([float(t['amount']) for t in transactions if float(t['amount']) < 0]))
    return build_lookup_from_transactions(transactions)


def build_lookup_from_transactions(transactions):
    lookup = {}
    for t in transactions:
        date = t['date']
        if date not in lookup:
            lookup[date] = {}
        date_transactions = lookup[date]
        amount = t['amount']
        if amount not in date_transactions:
            date_transactions[amount] = []
        amount_transactions = date_transactions[amount]
        amount_transactions.append(t)
    return lookup


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise Exception('pass in the folder you want to report on')
    folder = sys.argv[1]
    main(folder)
