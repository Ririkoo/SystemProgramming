from code.lays.parser import Parser
from code.lays.scanner import Scanner

if __name__ == '__main__':
    program = """
    c = 1;
    for(a = 1;a>0;a++){
        c = a+1;
    };

    """
    parser = Parser(Scanner(program))
    parser.parsed_tree.dump()
