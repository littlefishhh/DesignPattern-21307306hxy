import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Funny JSON Explorer')
    parser.add_argument('-f', '--file', required=True, help='JSON file')
    # parser.add_argument('-s', '--style', required=True, help='Rendering style')
    # parser.add_argument('-i', '--icons', required=True, help='Icon family')
    parser.add_argument('-s', '--style', choices=['tree', 'rectangle'], required=True, help='Rendering style')
    parser.add_argument('-i', '--icons', choices=['default', 'poker-face','circle','flower','star','crown','animal','rectangle','weather'], required=True, help='Icon family')
    return parser.parse_args()

def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

class JsonNode:
    def __init__(self, name, level=0, is_root=False,is_first=False, is_leaf=False,is_last=False):
        self.name = name
        self.level = level
        self.is_first=is_first
        self.is_root = is_root
        self.is_leaf = is_leaf
        self.is_last=is_last
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def render_node(self,  icons):
        raise NotImplementedError

    def render_leaf(self,  icons):
        raise NotImplementedError

    def render_container(self,  icons):
        raise NotImplementedError

class TreeStyleJsonNode(JsonNode):
    def __init__(self, node, is_last=True):
        super().__init__(node.name, node.level, node.is_root, node.is_first,node.is_leaf,node.is_last)
        self.children = node.children
        self.is_last = is_last

    def render_node(self, icons, prefix=""):
        if self.is_leaf:
            return self.render_leaf( icons, prefix)
        else:
            return self.render_container( icons, prefix)

    def render_container(self,  icons, prefix=""):
        lines = ""
        if self.level > 0:
            prefix = " "  * (self.level - 1)
            if self.is_last:
                prefix += "└─"
            else:
                prefix += "├─"
            lines = f"{prefix}{icons['node']}{self.name}\n"
        
        for i, child in enumerate(self.children):
            child = TreeStyleJsonNode(child, is_last=(i == len(self.children) - 1))
            lines += (" "  * (self.level - 1) + "│  " if not self.is_last else " " * 2 * (self.level - 1) + "   ") + child.render_node( icons, prefix).replace("\n", "\n" + (" " * 2 * (self.level - 1) + "│  " if not self.is_last else " " * 2 * (self.level - 1) + "   ")).rstrip() + "\n"

        return lines.rstrip("\n")

    def render_leaf(self, icons, prefix=""):
        prefix = " " * (self.level - 1)
        if self.is_last:
            prefix += "└─"
        else:
            prefix += "├─"
        return f"{prefix}{icons['leaf']}{self.name}\n"
    
class RectangleStyleJsonNode(JsonNode):
    def __init__(self, node, is_last=True):
        super().__init__(node.name, node.level, node.is_root, node.is_first, node.is_leaf,node.is_last)
        self.children = node.children
        self.is_last = is_last

    def render_node(self, icons, prefix=""):
        
        if self.is_leaf:
            return self.render_leaf(icons, prefix)
        else:
            return self.render_container(icons, prefix)

    def render_container(self,  icons, prefix=""):
        lines = ""
        if self.level > 0:
            prefix = "│ "  * (self.level - 1)
            if self.is_first:
                prefix += "┌─"
            else:
                prefix += "├─"
            lines = "\n"+f"{prefix}{icons['node']}{self.name}"
        for i, child in enumerate(self.children):
            child = RectangleStyleJsonNode(child, is_last=(i == len(self.children) - 1))
            lines +=  child.render_node(icons, prefix)

        return lines

    def render_leaf(self, icons, prefix=""):
        prefix = "│ " * (self.level - 1)
        prefix += "├─"
        return "\n"+f"{prefix}{icons['leaf']}{self.name}"


class IconFamily:
    def __init__(self, icon_type):
        self.icon_type = icon_type

    def get_icons(self):
        if self.icon_type == 'poker-face':
            return {'node': '♢', 'leaf': '♤'}
        elif self.icon_type == 'circle':
            return {'node': '○', 'leaf': '●'}
        elif self.icon_type == 'flower':
            return {'node': '❀ ', 'leaf': '✿ '}
        elif self.icon_type == 'recrangle':
            return {'node': '□ ', 'leaf': ' ■ '}
        elif self.icon_type == 'crown':
            return {'node': '♚ ', 'leaf': '♛ '}
        elif self.icon_type == 'star':
            return {'node': '☆ ', 'leaf': '★ '}
        elif self.icon_type == 'weather':
            return {'node': '☀️  ', 'leaf': '☁️  '}
        elif self.icon_type == 'animal':
            return {'node': '🐶  ', 'leaf': '🐱  '}
        else:
            return {'node': '', 'leaf': ''}

class StyleFactory:
    def __init__(self,root):
        raise NotImplementedError
    def render(self, icons):
        raise NotImplementedError

class TreeStyleFactory(StyleFactory):
    def __init__(self,root):
        self.root=TreeStyleJsonNode(root)
    def render(self, icons):
        output=self.root.render_node(icons)
        return output

class RectangleStyleFactory(StyleFactory):
    def __init__(self,root):
        self.root=RectangleStyleJsonNode(root)
    def render(self, icons):
        answer=self.root.render_node(icons)
        answerlist=answer.split('\n')
        answerlist=[item  for item in answerlist if item!='']
        max_length = max(len(line) for line in answerlist)+5
        answerlist[len(answerlist)-1]=answerlist[len(answerlist)-1].replace('│','└')
        answerlist[len(answerlist)-1]=answerlist[len(answerlist)-1].replace('├','┴')
        answerlist[len(answerlist)-1]=answerlist[len(answerlist)-1].replace(icons['leaf'],'cantbereplace')
        answerlist[len(answerlist)-1]=answerlist[len(answerlist)-1].replace(' ','─')
        answerlist[len(answerlist)-1]=answerlist[len(answerlist)-1].replace('cantbereplace',icons['leaf'])
        padded_lines = [line.ljust(max_length, '─') for line in answerlist]
        answer="\n"
        for i in range(len(padded_lines)):
            answer=answer+padded_lines[i]
            if (i==0): answer=answer+'┐'
            else: 
                if i==len(padded_lines)-1: answer=answer+'┘'
                else: answer=answer+'┤'
            answer=answer+"\n"
    
        return answer

class JsonFactoryRegister:
    def __init__(self, args):
        self.args = args

    def get_icon_family(self):
        return IconFamily(self.args.icons)

    def get_style_factory(self,root):
        if self.args.style == 'tree':
            return TreeStyleFactory(root)
        elif self.args.style == 'rectangle':
            return RectangleStyleFactory(root)
        else:
            raise ValueError("Unknown style")

class FunnyJsonExplorer:
    def __init__(self, args):
        self.args=args
        self.register=JsonFactoryRegister(args)
        self.icon_family = self.register.get_icon_family()
        self.is_first=False

    def create(self):
        data = load_json(self.args.file)
        self.root = self.build_node(data, is_root=True)
    
    def render(self):
        icons = self.icon_family.get_icons()
        self.style_factory = self.register.get_style_factory(self.root)
        output = self.style_factory.render(icons)
        print(output)

    def build_node(self, data, is_first=True,level=0, is_root=False,is_last=False):
        
        if is_root:
            name = "root"
            node_data = data
            self.is_first=True
        else:
            if isinstance(data, dict):
                name = next(iter(data.keys()))
                node_data = data[name]
            elif isinstance(data, str):
                name = data
                node_data = None
            else:
                name = data
                node_data = None

        node = JsonNode(name, level=level, is_first=is_first,is_root=is_root, is_leaf=node_data is None,is_last=is_last)
        # print(name)
        # print("son:  ",node_data)
        if node_data is not None :
            if isinstance(node_data, dict):
                for child_name, child_data in node_data.items():
                    if (is_root and is_first): 
                        child_node = self.build_node({child_name: child_data}, is_first=True, level=level+1)
                        is_first=False
                    else: child_node = self.build_node({child_name: child_data}, is_first=False, level=level+1)
                    self.is_first=False
                    node.add_child(child_node)
            elif isinstance(node_data, list):
                for child_data in node_data:
                    child_node = self.build_node(child_data, is_first=self.is_first, level=level+1)
                    self.is_first=False
                    node.add_child(child_node)
            elif isinstance(node_data, str):  
                child_node = self.build_node(node_data, is_first=self.is_first, level=level+1,is_last=True)
                self.is_first=False
                node.add_child(child_node)

        return node

def main():
    args = parse_args()
    explorer = FunnyJsonExplorer(args)
    explorer.create()
    explorer.render()

if __name__ == "__main__":
    main()
