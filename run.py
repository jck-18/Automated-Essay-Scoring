import os
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Run Essay Scoring App in Streamlit or API mode")
    parser.add_argument("--mode", choices=["streamlit", "api", "both"], default="streamlit", 
                        help="Run in Streamlit mode, API mode, or both")
    parser.add_argument("--port", type=int, default=8000,
                        help="Port for the API server (default: 8000)")
    parser.add_argument("--streamlit-port", type=int, default=8501,
                        help="Port for Streamlit (default: 8501)")
    
    args = parser.parse_args()
    
    if args.mode == "streamlit":
        # Run Streamlit only
        cmd = f"streamlit run app.py --server.port={args.streamlit_port}"
        subprocess.run(cmd, shell=True)
    
    elif args.mode == "api":
        # Run only the API server
        os.environ["ENABLE_API"] = "True"
        os.environ["PORT"] = str(args.port)
        import app
        
    elif args.mode == "both":
        # Run both Streamlit and API
        os.environ["ENABLE_API"] = "True"
        os.environ["PORT"] = str(args.port)
        
        # Start API in a separate process
        from multiprocessing import Process
        def run_api():
            import app
        
        api_process = Process(target=run_api)
        api_process.start()
        
        # Start Streamlit
        cmd = f"streamlit run app.py --server.port={args.streamlit_port}"
        subprocess.run(cmd, shell=True)
        
        # Clean up API process when Streamlit exits
        api_process.terminate()
        api_process.join()

if __name__ == "__main__":
    main() 