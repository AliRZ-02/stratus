import json
import re
from datetime import datetime
from typing import Callable, Type
from collections import Counter, defaultdict

from crewai.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

from stratus.tools.aiopslab.helper import AIOpsLabHelper


class GetLogsToolInput(BaseModel):
    namespace: str = Field(
        title="Namespace",
        description="The Kubernetes namespace from which to fetch logs.",
    )
    service: str = Field(
        title="Service",
        description="The service name for which to fetch logs.",
    )


class GetLogsTool(BaseTool):
    name: str = "get_logs"
    description: str = (
        "This tool helps you fetch logs from a specified Kubernetes namespace and service. "
        "Please provide 'namespace' and 'service' arguments, and the tool will fetch the logs."
    )
    args_schema: Type[BaseModel] = GetLogsToolInput
    generator: AIOpsLabHelper | None = None
    cache_function: Callable = lambda _args=None, _result=None: False

    def __init__(self, generator: AIOpsLabHelper | None = None):
        super().__init__()
        self.generator = generator

    def _run(self, namespace: str, service: str) -> str:
        if self.generator is None:
            return f'No generator linked. Please output ```get_logs("{namespace}", "{service}")``` directly to send it to the orchestrator.'

        # print(f'Fetching logs for namespace: {namespace}, service: {service}')
        result = self.generator.send(f'```\nget_logs("{namespace}", "{service}")\n```')
        # print('Got result:', len(result))
        filtered = self._filter_logs(result.replace("Please take the next action", ""))
        # print(f'Filtered Result: {len(filtered)}')
        return filtered + "\n\n These logs are truncated to pay extra attention to each name, value or error provided since it may have occurred more than once.\n\nPlease take the next action"
    
    def _filter_logs(self, logString):
        logs = logString.split("\n")
        candidates = set()
        
        N = 0
        while N < len(logs):
            if N in candidates:
                N += 1
                continue
            
            logLine = logs[N]
            if not logLine:
                N += 1
                continue

            if N >= len(logs) - 5:
                candidates.add(N)
            elif self._has_failure_keywords(logLine):
                for i in range(N - 3, N + 1):
                    candidates.add(i)
            
            N += 1
        
        context = list()
        tsList = defaultdict(list)
        for lineNum in sorted(list(candidates)):
            line = logs[lineNum].strip()
            if line == r"\n":
                continue
            newLine, ts = self._extract_line_information(line)
            context.append(newLine)
            if ts is not None:
                tsList[newLine].append(ts.strftime(r"%Y-%m-%dT%H:%M:%S.%f"))
        
        contextCounter = Counter(context)
        output = []
        seen = set()
        for line in context:
            if line in seen:
                continue
            
            timeInfo = ""
            if line in tsList:
                if len(tsList[line]) > 1:
                    timeInfo = f" from {tsList[line][0]} to {tsList[line][-1]}"
                else:
                    timeInfo = f" at {tsList[line][0]}"
            
            output.append(line + f": Seen {contextCounter.get(line)} times{timeInfo}")
            seen.add(line)
        
        return "\n".join(output)

    def _has_failure_keywords(self, line):
        # I got this from the logsage paper pseudocode
        KEYWORDS = ["fatal",  "fail", "panic", "error", "exit", "kill", "err", "missing", "exception", "refuse"]

        toSearch = line.lower()
        for word in KEYWORDS:
            if word in toSearch:
                return True
        
        return False
    
    def _strip_common(self, logs):
        logs = re.sub(r'\b[0-9a-f]{8}-[0-9a-f\-]{27}\b', '<UUID>', logs)
        logs = re.sub(r'0x[0-9a-fA-F]+', '<ADDR>', logs)
        logs = re.sub(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', '<MAC>', logs)
        logs = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}[\.Z]\d*', '<TS>', logs)

        return logs.replace(r"\n", '').strip()
    
    def _extract_line_information(self, line):
        # print((line))
        jsonData = None
        try:
            jsonData = json.loads(line)
        except:
            pass
        
        if jsonData:
            timeStamp = None
            filtered_msg = line
            try:
                if "time" in jsonData:
                    timeString = jsonData["time"]
                    try:
                        format_1 = r"%Y-%m-%dT%H:%M:%SZ"
                        timeStamp = datetime.strptime(timeString, format_1)
                        filtered_msg = self._strip_common(jsonData["message"].replace(timeString, '<TS>'))

                        return filtered_msg, timeStamp
                    except:
                        pass
                
                if "t" in jsonData and "$date" in jsonData["t"]:
                    timeString = jsonData["t"]["$date"]
                    try:
                        format_2 = r"%Y-%m-%dT%H:%M:%S.%f%z"
                        timeStamp = datetime.strptime(timeString, format_2)
                        filtered_msg = jsonData["msg"].replace(timeString, '<TS>')

                        if "attr" in jsonData:
                            for key in jsonData["attr"]:
                                if isinstance(jsonData["attr"][key], str) and jsonData["attr"][key]:
                                    filtered_msg = filtered_msg + f" -{key}- " + jsonData["attr"][key]

                        return self._strip_common(filtered_msg), timeStamp
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
        try:
            format_1_regex = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
            match = re.findall(format_1_regex, line)[0]
            filtered_msg = line.replace(match, '<TS>')

            return self._strip_common(filtered_msg), datetime.strptime(match, r"%Y-%m-%dT%H:%M:%SZ")
        except:
            try:
                format_2_regex = r"\d{4}-[A-Za-z]{3}-\d{2} \d{2}:\d{2}:\d{2}\.\d+"
                match = re.findall(format_2_regex, line)[0]
                filtered_msg = line.replace(match, '<TS>')

                return self._strip_common(filtered_msg), datetime.strptime(match, r"%Y-%b-%d %H:%M:%S.%f")
            except:
                pass
        
        return self._strip_common(line), None
