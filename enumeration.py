import requests
import argparse
import time
import bs4
import cutt_file_parts as cpg


class EnumerationWeb:
    """Class for enumerate the directory or file"""

    def __init__(self, url: str):
        """Keyword arguments:
            url -- the url to web site."""
        self.url = url

    def request_test(self):
        """Return the boolean.
            Check if the request is good."""
        request = requests.get(self.url)
        if request.ok:
            return True
        return False

    def enumeration(self, element: str):
        """Opens the file is looped on each line.
            Make a request element to the website."""
        r = requests.get(self.url+element.strip())
        if r.ok or r.status_code == 403:
            print(r.url, "--->", r.status_code)


class EnumerationSiteMap(EnumerationWeb):
    def __init__(self, url: str):
        super().__init__(url+"/sitemap-page.xml")
        self.links = []

    def get_all_links(self):
        response = requests.get(self.url)
        if response.ok:
            soup = bs4.BeautifulSoup(response.content, "lxml")
            for link in soup.find_all("loc"):
                self.links.append(link.string)
        return None

    def enumeration_links(self, element: str):
        for link in self.links:
            r = requests.get(link+element.strip())
            if r.ok or r.status_code == 403:
                print(r.url, "--->", r.status_code)


def parser_argument():
    """Return the args variable.
        Parse the argument for command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-w', '--wordlists', help="Enter the relative path your wordlists", type=str, required=True)
    parser.add_argument(
        '-u', "--url", help="Enter the url to web site", type=str, required=True)
    parser.add_argument(
        "-t", help="Enter the number of the thread", type=int, default=100)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    argument = parser_argument()
    start = time.perf_counter()

    start_enum = EnumerationWeb(argument.url)
    sitemap_enum = EnumerationSiteMap(argument.url)
    
    element_file, before_last = cpg.before_last_lenght_file_element(
        argument.wordlists)
    result_calcul = cpg.calcul(len(element_file), before_last)
    sitemap_enum.get_all_links()

    if start_enum.request_test():
        for element in cpg.cutt(element_file, result_calcul): 
            cpg.thread_executor(start_enum.enumeration, element, argument.t)

    if sitemap_enum.request_test():
        print("Passage au site map...")
        for element in cpg.cutt(element_file, result_calcul):
            cpg.thread_executor(sitemap_enum.enumeration_links, element, argument.t)

    print(time.perf_counter()-start)