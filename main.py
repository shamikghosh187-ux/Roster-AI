import argparse
import os

def parse_args():
    parser=argparse.ArgumentParser(description="Roster AI desktop assistant")
    parser.add_argument("--provider",choices=("groq","gemini","xai","claude"))
    parser.add_argument("--input",choices=("auto","voice","text"))
    parser.add_argument("--wake",choices=("auto","on","off"))
    parser.add_argument("--ui",action="store_true",help="launch the full desktop workspace")
    parser.add_argument("--list-providers",action="store_true")
    parser.add_argument("--doctor",action="store_true",help="run installation and dependency diagnostics")
    return parser.parse_args()

def main():
    args=parse_args()
    if args.list_providers:
        print("Supported providers: groq, gemini, xai, claude"); return
    if args.doctor:
        from roster.doctor import diagnose, format_report
        print(format_report(diagnose()))
        return
    if args.provider: os.environ["ROSTER_PROVIDER"]=args.provider
    if args.input: os.environ["ROSTER_INPUT_MODE"]=args.input
    if args.wake: os.environ["ROSTER_WAKE_MODE"]=args.wake
    if args.ui:
        from roster.ui.app import launch
        raise SystemExit(launch())
    from roster.core import Roster
    Roster().run()

if __name__=="__main__":
    main()
