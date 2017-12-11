import os
import re
from pzhe.Token import Token 

TOKEN_TYPE = ['ID', 'NUMBER', 'KEYWORD','OPERATOR', 'DELIMITER', 'OTHERS']
KEYWORD_SET = ['if', 'else', 'do', 'while', 'for' ,'return']
OPERATOR_SET = ['=', '&', '<', '>', '++', '--',
                '+', '-', '*', '/', '>=', '<=', '!=']
DELIMITER_SET = ['(', ')', '{', '}', '[', ']', ',', '\"', ';']

class Scanner:
    
    def __init__(self,inputfile):
        self.inputfile = inputfile
        self.token_list = []

    def print_list(self):
        for item in self.token_list:
            print(item.token+"["+item.typename+"]")

    
    def is_keyword(self,token):
        for each_word in KEYWORD_SET:
            if each_word == token:
                return True
        return False
    
    def is_useless(self,index ,content):
        return content[index] == ' ' or content[index] == '\t' or content[index] == '\n' or content[index] == '\r'
        #if(content[index] == ' ' or content[index] == '\n' 
        #    or content[index] == '\t' or content[index] == '\r'):
        #    return True
        #return False

    def skip_useless_char(self,index ,content):
        #print(len(content))
        while index < len(content):
            #print(index)
            if(self.is_useless(index,content)):
                index = index + 1
            else:
                break
        return index

   # def tokenization(line_str):
    
    def run_scan(self):
        file_reader=open(self.inputfile,'r')
        file_content=file_reader.read()
        cur_index = 0
        cur_index = self.skip_useless_char(cur_index,file_content)
        while cur_index < len(file_content):
            # DIGIT TYPE DETECT
            if(file_content[cur_index].isdigit()):
                each_token=''
                while(cur_index < len(file_content)):
                    if(file_content[cur_index].isdigit() or 
                        (file_content[cur_index] == '.' and file_content[i + 1].isdigit())):
                        each_token = each_token + file_content[cur_index]
                        cur_index = cur_index +1
                    else:
                        break
                self.token_list.append(Token('NUMBER', each_token))
                cur_index = self.skip_useless_char(cur_index,file_content)
            
            # ID or KEYWORD TYPE DETECT
            elif(file_content[cur_index] == '_' or file_content[cur_index].isalpha()):
                each_token=''
                while(cur_index < len(file_content)):
                    if(file_content[cur_index].isdigit() or 
                        (file_content[cur_index] == '_' 
                        or file_content[cur_index].isalpha() 
                        or file_content[cur_index].isdigit()
                        )):
                        each_token = each_token + file_content[cur_index]
                        cur_index = cur_index +1
                    else:
                        #print('break!')
                        break
                if self.is_keyword(each_token):
                    self.token_list.append(Token('KEYWORD', each_token))
                else:
                    self.token_list.append(Token('ID', each_token))
                cur_index = self.skip_useless_char(cur_index,file_content)
            
            # DELIMITER TYPE DETECT
            elif(file_content[cur_index] in DELIMITER_SET):
                self.token_list.append(Token('DELIMITER', file_content[cur_index]))
                cur_index = self.skip_useless_char(cur_index+1,file_content)
            

            # OPERATOR TYPE DETECT
            elif file_content[cur_index] in OPERATOR_SET:
                if ((file_content[cur_index] == '+' or file_content[cur_index] == '-') 
                    and file_content[cur_index + 1] == file_content[cur_index]):
                    self.token_list.append(Token('OPERATOR', file_content[cur_index]+file_content[cur_index+1]))
                    cur_index = self.skip_useless_char(cur_index+2 ,file_content)
                elif (file_content[cur_index] == '<' or file_content[cur_index] == '>') and file_content[cur_index + 1] == '=':
                    self.token_list.append(Token('OPERATOR', file_content[cur_index]+ '='))
                    cur_index = self.skip_useless_char(cur_index+2 ,file_content)
                else:
                    self.token_list.append(Token('OPERATOR', file_content[cur_index]))
                    cur_index = self.skip_useless_char(cur_index+1,file_content)
            else:
                self.token_list.append(Token('OTHERS', file_content[cur_index]))
                cur_index = self.skip_useless_char(cur_index+1,file_content)

    