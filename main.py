import argparse
import os


def parse_args():
    parser = argparse.ArgumentParser(description='Roster AI desktop assistant')
    parser.add_argument('--provider', choices=('groq', 'gemini', 'xai', 'claude'), help='AI provider')
    parser.add_argument('--input', choices=('auto', 'voice', 'text'), help='input mode')
    parser.add_argument('--list-providers', action='store_true', help='show supported providers and exit')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list_providers:
        print('Supported providers: groq, gemini, xai, claude')
        return
    if args.provider:
        os.environ['ROSTER_PROVIDER'] = args.provider
    if args.input:
        os.environ['ROSTER_INPUT_MODE'] = args.input
    from roster.core import Roster
    Roster().run()


if __name__ == '__main__':
    main()
