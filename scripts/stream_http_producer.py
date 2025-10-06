#!/usr/bin/env python3
"""
Simple example that posts a satellite CSV file to the upload server (/upload_sat).
Usage:
  python scripts/stream_http_producer.py --file example.csv --event Valdivia_1960 --token devtoken
"""
import argparse
import requests


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--file', '-f', required=True)
    p.add_argument('--event', '-e', required=True)
    p.add_argument('--url', default='http://localhost:5001/upload_sat')
    p.add_argument('--token', default='devtoken')
    p.add_argument('--run-pipeline', action='store_true')
    return p.parse_args()


def main():
    args = parse_args()
    headers = {'Authorization': f'Bearer {args.token}'} if args.token else None
    params = {'event': args.event}
    if args.run_pipeline:
        params['run_pipeline'] = 'true'
    with open(args.file, 'rb') as f:
        files = {'sat': (args.file, f, 'text/csv')}
        r = requests.post(args.url, files=files, data={'event': args.event}, headers=headers, params=params)
        print('STATUS', r.status_code)
        print(r.text)


if __name__ == '__main__':
    main()
