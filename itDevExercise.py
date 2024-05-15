import requests
import json
from datetime import datetime, timedelta


class TimeSheet:
    def __init__(self, _api_uri):
        self._api_response = json.loads(requests.get(_api_uri).text)
        self._headers = []
        self._list_items = {}
        self.dates = []
        self._buildHeaders()

    def _buildHeaders(self):
        for job in self._api_response:
            project_name = job["project"]
            if project_name not in self._headers:
                self._headers.append(project_name)

    def _append_job(self, entry_date, project):
        if entry_date not in self._list_items:
            self._list_items[entry_date] = {}
            for project_title in self._headers:
                self._list_items[entry_date][project_title] = 0
        if project not in self._list_items[entry_date]:
            self._list_items[entry_date][project] = 0
        self._list_items[entry_date][project] += 1

    def _process_date_range(self, first, last, project):
        firstDay = datetime.strptime(first, "%Y-%m-%d").date()
        lastDay = datetime.strptime(last, "%Y-%m-%d").date()
        numDays = timedelta(1)
        while firstDay <= lastDay:
            entryDate = str(firstDay.strftime("%Y-%m-%d"))
            self._append_job(entryDate, project)
            firstDay += numDays
            if entryDate not in self.dates:
                self.dates.append(entryDate)

    def _print_header(self):
        _header_text = ""
        for item in self._headers:
            _header_text += "," + item
        return _header_text[1:] + "\n"

    def _process_job(self, job):
        _start_date = job["start"]
        _end_date = job["end"]
        _project_name = job["project"]
        if _start_date != _end_date:
            self._process_date_range(_start_date, _end_date, _project_name)
        else:
            self._append_job(_start_date, _project_name)
            if _start_date not in self.dates:
                self.dates.append(_start_date)
        self.dates.sort()

    def generate_csv(self):
        _csv_string = "date,"
        _csv_string += self._print_header()
        for job in self._api_response:
            self._process_job(job)
        for row in self.dates:
            _csv_string += row
            for project in self._headers:
                _csv_string += "," + str(self._list_items[row][project])
            _csv_string += "\n"
        self.dates.sort()
        return _csv_string

    def send_response(self, payload):
        _headers = {
            'Content-type': 'text/csv',
            'upload-key': '95341ee6-4efc-4148-9619-b4b800b9eeb6'
        }
        put_response = requests.put("https://accounts.bluefruit.software/upload/51m0nt35t.csv", headers=_headers, data=payload)
        print(put_response.json())


time_sheet = TimeSheet("https://timetracking.bluefruit.software/api/days")
time_sheet.send_response(time_sheet.generate_csv())
