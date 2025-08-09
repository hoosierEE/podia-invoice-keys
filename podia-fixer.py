import csv
import argparse


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('podia', type=str, help='the Podia csv')
    p.add_argument('stripe', type=str, help='the Stripe csv')
    return p.parse_args()


def csv_to_dict(filename: str) -> (dict, csv.Dialect):
    with open(filename) as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        return ({x[0]:x[1:] for x in zip(*csv.reader(f, dialect))}, dialect)


def main(podia_path, stripe_path):
    podia, _ = csv_to_dict(podia_path)
    stripe, dialect = csv_to_dict(stripe_path)

    i2d = dict(zip(podia['Invoice #'], podia['Items']))
    desc = [i2d.get(x[9:], x) if x.startswith('Invoice #') else x for x in stripe['Description']]
    desc = []
    for x,y in zip(stripe['Description'],stripe['Status']):
        if x.startswith('Invoice #'):
            desc.append('N/A' if y == 'Failed' else i2d[x[9:]])
        else:
            desc.append(x)

    stripe['Description'] = desc  # replace column

    with open('output.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=stripe.keys(), dialect=dialect, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for t in zip(*stripe.values()):
            writer.writerow(dict(zip(stripe, t)))

    return stripe



if __name__ == "__main__":
    args = parse_args()
    main(args.podia, args.stripe)
