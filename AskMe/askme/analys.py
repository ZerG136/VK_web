import subprocess

def run_benchmark(url, tool="ab", count=1000, concurrency=10):
    if tool == "ab":
        command = f"ab -n {count} -c {concurrency} {url}"
    elif tool == "wrk":
        command = f"wrk -t12 -c400 -d30s {url}"
    else:
        raise ValueError("Unknown tool. Use 'ab' or 'wrk'.")
    
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode()

def main():
    urls = [
        "http://localhost/static/templates/ask.html",
        "http://localhost:8000/static//templates/ask.html",
        "http://localhost:8000/dynamic/",
        "http://localhost/dynamic/",
        "http://localhost/cached/"
    ]
    
    tool = "ab"
    
    for url in urls:
        print(f"Running benchmark for {url} using {tool}...")
        result = run_benchmark(url, tool)
        print(result)

if __name__ == "__main__":
    main()
