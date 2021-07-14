import re
import sys
import os
from typing import List
from enum import Enum

class QuestionType(Enum):
  NULL = 0
  MULTIPLE_CHOICE = 1
  TRUE_FALSE = 2
  MATCHING = 3
  SHORT_ANSWER = 4
  ESSAY = 5


def parse_tex_string(lines: List[str], index: int, is_equation_open: bool, 
                      filename: str, is_code_block_open: bool):
  new_is_code_block_open = parse_tex_code_blocks(lines, index, is_code_block_open)
  if new_is_code_block_open or is_code_block_open:
    return is_equation_open, None, new_is_code_block_open  
  parse_tex_special_symbols_and_inline_code(lines, index)
  parse_tex_line_breaks(lines, index)
  image_to_add = parse_tex_image(lines, index, filename)
  is_equation_open = parse_tex_equation(lines, index, is_equation_open)
  
  return is_equation_open, image_to_add, new_is_code_block_open


def parse_tex_special_symbols_and_inline_code(lines: List[str], index: int):
  # inline_code_regex = "\`(?P<code>.+)\`"
  line = lines[index]
  split_lines = line.split('`')
  final_string = ''
  # Inline `code` has `back-ticks around` it.
  for _idx, line in enumerate(split_lines):
    if _idx % 2 == 0:
      line = re.sub(r'\\(?P<first_char>[^_$()])', r'\\\\'+ '\\g<first_char>', line)
      line = re.sub("_", "\_", line)
      line = re.sub("\$", "\$", line)
    else:
      line = f'\\mintinline{{sql}}{{{line}}}'

    final_string += line

  lines[index] = final_string


def parse_tex_equation(lines: List[str], index: int, is_equation_open: bool):
  start_equation_regex = r"\\\("

  if not is_equation_open:
    output, count = re.subn(start_equation_regex, "$", lines[index])
    if count > 0:
      is_equation_open = True 
      lines[index] = output

  if is_equation_open:
    split_list = lines[index].split('\)')
    backslash_parsed_string = re.sub(r'\\\\', r'\\', split_list[0])
    
    if len(split_list) > 1:
      backslash_parsed_string += '$' + split_list[1] 
      is_equation_open = False

    lines[index] = backslash_parsed_string

  return is_equation_open


def parse_tex_image(lines: List[str], index: int, filename: str):
  image_regex = "!\[.*\]\(fig-\d+.jpg \".*\"\)"
  line = lines[index]
  # para cada imagem, adicionar um include graphics
  # ![Texto Alternativo](fig-0000.jpg "Legenda")
  line_string, count = re.subn(image_regex, '', line)
  if count:
    parsed_string = line.split('(')[1]
    filename_and_caption = parsed_string.split('\"')
    figure_filename = filename_and_caption[0]
    figure_caption = filename_and_caption[1].split("\")")[0]
    figure_fullpath = f'{filename}_figuras/{figure_filename}'.strip()

    lines[index] = line_string

    return [
      '\\begin{figure}[H]\n',
      '\t\\begin{center}\n',
      f'\t\t\\includegraphics[width=0.5\\textwidth]{{{figure_fullpath}}}\n',
      f'\t\t\\caption{{{figure_caption}}}\n' if len(figure_caption) > 1 else '',
      '\t\\end{center}\n',
      '\\end{figure}\n'
    ]


def parse_tex_line_breaks(lines: List[str], index: int):
  lines[index] = re.sub('<br/>', '\n', lines[index])


def parse_tex_code_blocks(lines: List[str], index: int, is_code_block_open: bool):
  start_code_block_regex = "\`\`\`(?P<language_highlight>\w*)"

  if not is_code_block_open:
    line = lines[index]
    split_list = line.split("```")
    if len(split_list) > 1:
      code_line = "```" + split_list[1]
      code_block_match = re.match(start_code_block_regex, code_line) 
      language_highlight_group = code_block_match.group('language_highlight')
      language_highlight = language_highlight_group if len(language_highlight_group) > 0 else 'javascript'
      output, count = re.subn(start_code_block_regex, f'\\\\begin{{minted}}{{{language_highlight}}}', code_line)
      output = split_list[0] + output
      if count > 0:
        is_code_block_open = True 
        lines[index] = output

  if is_code_block_open:
    line = lines[index]
    split_list = line.split("```")
    backslash_parsed_string = re.sub(r'\\\\', r'\\', split_list[0])
    
    if len(split_list) > 1:
      backslash_parsed_string += f'\\end{{minted}} {split_list[1]}'
      is_code_block_open = False

    lines[index] = backslash_parsed_string

  return is_code_block_open


def update_tex_question_title_with_type(last_question_index: int, output_list: List[str], question_type: QuestionType):
  if question_type is QuestionType.MULTIPLE_CHOICE:
    output_list[last_question_index] += f' $|$ \\textbf{{Objetiva}}'
  elif question_type is QuestionType.ESSAY:
    output_list[last_question_index] += f' $|$ \\textbf{{Dissertativa}})\n'
  elif question_type is QuestionType.NULL and last_question_index != 0:
    output_list[last_question_index] += ')\n'


# MUST IMPORT \usepackage{enumitem}
def MD_to_tex(filename: str):
  print("Converting to TeX...")
  
  preamble_filename = os.path.join('moodle_question_tool', 'core', 'preamble.tex')
  converted_filename = filename.replace(".txt", ".tex")
  output_file = open(converted_filename, "w")
  output_list = []

  filename_without_extension = os.path.basename(filename).split('.')[0]
  paths = re.split("_", filename_without_extension)

  test_type = paths[0] if len(paths) >= 1 else 'PROVA' 
  test_year = paths[1] if len(paths) >= 2 else 'ANO'
  test_course = paths[2] if len(paths) >= 3 else 'CURSO'
  document_title = f"\\LARGE \\textbf{{Prova {test_type} {test_year}\\\ {test_course} \\\}}"

  with open(preamble_filename) as file:
    lines = file.readlines()
    for index in range(len(lines) - 1):
      if lines[index] == '\\LARGE \\textbf{Prova Enade 2019\\\\Engenharia de Computação \\\\}\n':
        lines[index] = document_title
    
    output_file.writelines(lines)

  alternative_regex = '(-[a-e].)'
  question_regex = '(#Q)\d+'

  should_close_enumerate = False
  is_enumerate_open = False

  output_list.append("\\begin{questions}\n")

  with open(filename) as file:
    lines = file.readlines()
    
    index = 0
    line = ""
    image_to_add = []
    is_equation_open = False
    is_code_block_open = False
    is_add_image_pending = False
    last_question_index = 0
    last_question_type = QuestionType.NULL
    while index < len(lines):
      is_equation_open, image_to_add, is_code_block_open = parse_tex_string(lines, index, is_equation_open, filename_without_extension, is_code_block_open)
      if image_to_add:
        is_add_image_pending = True

      line = lines[index]

      # para cada marcação de questão, escrever um \question
      if re.match(question_regex, line):
        update_tex_question_title_with_type(last_question_index, output_list, last_question_type)
        last_question_type = QuestionType.ESSAY
        output_list.append(f"\\question (\\textbf{{{test_type}}} $|$ \\textbf{{{test_course}}}-\\textbf{{{test_year}}}")
        last_question_index = len(output_list) - 1
        index += 1
      # para cada marcação de alternativa adicionar um item do enumerate
      elif re.match(alternative_regex, line):
        # se é a primeira questão, abrir um enumerate
        if re.match("(-a.)", line):
          is_enumerate_open = True
          output_list.append("\t\\begin{enumerate}[label=\\alph*)]\n")
          update_tex_question_title_with_type(last_question_index, output_list, QuestionType.MULTIPLE_CHOICE)
          last_question_type = QuestionType.NULL

        string_to_append = ""
        # remove -a.
        string_to_append = re.sub(alternative_regex, "", line)

        while \
            index < (len(lines) - 2) and not re.match(alternative_regex, lines[index + 1]) and \
            not re.match(question_regex, lines[index + 1]):
          index += 1

          if image_to_add:
            is_add_image_pending = False
            string_to_append += ''.join(image_to_add)

          is_equation_open, image_to_add, is_code_block_open = parse_tex_string(lines, index, is_equation_open, filename_without_extension, is_code_block_open)

          line = lines[index]
          if (line != '\n'):
            string_to_append += line

          if image_to_add:
            is_add_image_pending = False
            string_to_append += ''.join(image_to_add)

        if image_to_add:
          is_add_image_pending = False
          string_to_append += ''.join(image_to_add)

        # se a próxima linha é uma questão, fechar o enumerate
        if index < (len(lines) - 2) and re.match(question_regex, lines[index + 1]):
          should_close_enumerate = True 
        else:
          should_close_enumerate = False
          
        index += 1
        output_list.append(f"\t\t\\item {string_to_append}")
      # caso não tenha marcação, apenas escrever diretamente
      else:
        if (line != ''):
          output_list.append(line)
        index += 1

      if should_close_enumerate:
        should_close_enumerate = False
        output_list.append("\t\\end{enumerate}\n\n")

      if is_add_image_pending and image_to_add:
        is_add_image_pending = False
        output_list.extend(image_to_add)    
        
    update_tex_question_title_with_type(last_question_index, output_list, last_question_type)
  
  if is_enumerate_open:
    is_enumerate_open = False
    output_list.append("\t\\end{enumerate}\n\n")

  output_list.append("\\end{questions}\n\n")
  output_list.append("\\end{document}\n")

  output_file.writelines(output_list)
  output_file.close()

  # mv output to correct folder
  output_dir = os.path.join(os.path.dirname(converted_filename), 'output')
  print(output_dir)
  os.system(f'mkdir {output_dir}')
  os.system(f'mv "{converted_filename}" "{output_dir}"')

  return output_dir


def MD_to_GIFT():
  print("GIFT NOT IMPLEMENTED YET.")


def is_64bits():
  return sys.maxsize > 2**32
  

def pdf_to_text(filename):
  xpdf_tools_binaries = os.path.join('moodle_question_tool', 'core', 'xpdf-tools-linux-4.03', 'bin64')
  pdftotext_binary = os.path.join(xpdf_tools_binaries, 'pdftotext')
  pdfimages_binary = os.path.join(xpdf_tools_binaries, 'pdfimages')

  # run pdftotext
  os.system(f'{pdftotext_binary} -raw {filename}')
  # mv output to correct folder
  output_dir = os.path.join(os.path.dirname(filename), 'output')
  os.system(f'mkdir {output_dir}')
  os.system(f'mv {filename.split(".pdf")[0]}.txt {output_dir}')

  figures_path = os.path.join(output_dir, f'{os.path.basename(filename).split(".pdf")[0]}_figuras')
  os.system(f'mkdir {figures_path}')

  figures_path = os.path.join(figures_path, 'fig')
  # run pdfimages
  os.system(f'{pdfimages_binary} -j {filename} {figures_path}')

  return output_dir