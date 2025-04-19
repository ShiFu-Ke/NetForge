import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


def create_qrc(resource_dir, output_file, prefix="/gallery"):
    # 创建XML结构
    rcc = Element('RCC')
    qresource = SubElement(rcc, 'qresource', attrib={'prefix': prefix})

    # 遍历资源目录
    for root, dirs, files in os.walk(resource_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, resource_dir).replace(os.sep, '/')
            SubElement(qresource, 'file').text = rel_path

    # 生成美化后的XML并移除XML声明
    xml_str = minidom.parseString(tostring(rcc)).toprettyxml(indent='  ', encoding='utf-8')
    # 分割字节串并跳过第一行（XML声明）
    xml_without_decl = b'\n'.join(xml_str.splitlines()[1:])

    # 写入文件
    with open(output_file, 'wb') as f:
        f.write(xml_without_decl)


# 生成resources.qrc文件
create_qrc(resource_dir='../resource/', output_file='../resource/resource.qrc')
os.system("pyrcc5 ../resource/resource.qrc -o ../common/resource.py")
os.remove("../resource/resource.qrc")