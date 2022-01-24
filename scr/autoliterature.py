# -*- coding: utf-8 -*- 
import argparse
import os
import re
import time
import logging

from modules import FolderMoniter, PatternRecognizer, MetaExtracter
from modules import UrlDownload, note_modified

# log config
logging.basicConfig()
logger = logging.getLogger('Sci-Hub')
logger.setLevel(logging.DEBUG)


def set_args():
    parser = argparse.ArgumentParser(description="AutoLiterature")
    parser.add_argument('-p', '--root_path', type=str, default='../note', help="The path to the folder.")
    parser.add_argument("-o", "--output_path", type=str, default='../pdf', help="The path to the pdf folder.")
    parser.add_argument('-t', '--interval_time', type=int, default=1, help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 


def main():
    args = set_args()
    root_path = args.root_path 
    interval_time = args.interval_time

    # init 
    folder_moniter = FolderMoniter(root_path)
    pattern_recog = PatternRecognizer(r'- \[.*\]')
    meta_extracter = MetaExtracter()
    url_download = UrlDownload()

    while True:
        modified_items = folder_moniter.file_md5_update()
        for md_file, md_md5 in modified_items.items():
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            m = pattern_recog.findall(content)
            if m:
                replace_dict = dict()

                for literature in m:
                    literature_id = literature.split('[')[-1].split(']')[0]
                    
                    # Fetch data
                    try:
                        bib_dict = meta_extracter.id2bib(literature_id)
                        if "pdf_link" in bib_dict.keys():
                            pdf_dict = url_download.fetch(bib_dict["pdf_link"])
                            if not pdf_dict:
                                pdf_dict = url_download.fetch(literature_id)
                        else:
                            pdf_dict = url_download.fetch(literature_id)

                        # Upload attachment and generate shared link
                        if "\n" in bib_dict["title"]:
                            bib_dict["title"] = re.sub(r' *\n *', ' ', bib_dict["title"])

                        bib_dict["title"] = bib_dict["title"].replace(":", "：")

                        if bib_dict["type"] == "arxiv":
                            month = str(literature_id).split(".")[0][-2:]
                            pdf_name = f"【{bib_dict['year']}-{month}】" + bib_dict['title'] + '.pdf'
                        else:
                            pdf_name = f"【{bib_dict['year']}】" + bib_dict['title'] + '.pdf'
                        logger.info(pdf_name)
                        pdf_path = f"{args.output_path}/{pdf_name}"
                        pdf_abs_path = os.path.abspath(pdf_path).replace("\\", "/")
                        if pdf_dict:
                            with open(pdf_path, mode="wb") as f:
                                f.write(pdf_dict['pdf'])

                            logger.info("save pdf file, done!!")

                        if 'cited_count' in bib_dict.keys():
                            replaced_literature = "- **{}**. {} et.al. **{}**, **{}**, ([pdf]({}))([link]({})), (Citations **{}**).".format(
                                bib_dict['title'], bib_dict["author"].split(" and ")[0], bib_dict['journal'], 
                                bib_dict['year'], pdf_abs_path, bib_dict['url'], bib_dict["cited_count"]
                                )
                        else:
                            replaced_literature = "- **{}**. {} et.al. **{}**, **{}**, ([pdf]({}))([link]({}))\n\t> {}.".format(
                                bib_dict['title'], bib_dict["author"].split(" and ")[0], bib_dict['journal'], 
                                bib_dict['year'], pdf_abs_path, bib_dict['url'], bib_dict["summary"]
                                )

                        replace_dict[literature] = replaced_literature
                    except:
                        print("")

                # Modified note
                if replace_dict:
                    note_modified(pattern_recog, md_file, **replace_dict)

        time.sleep(interval_time)


if __name__ == "__main__":
    main()
