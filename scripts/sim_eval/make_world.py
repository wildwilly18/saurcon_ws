#!/usr/bin/env python3
"""Generate a test scenario without modifying the reference world."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=Path)
    p.add_argument('--no-markers',action='store_true')
    p.add_argument('--x',type=float,default=-1);p.add_argument('--y',type=float,default=0)
    p.add_argument('--yaw',type=float,default=0)
    a=p.parse_args()
    source=Path(__file__).resolve().parents[2]/'src/middle_earth/worlds/racetrack.world'
    tree=ET.parse(source);world=tree.getroot().find('world')
    for element in list(world):
        name=element.get('name','')+' '+element.findtext('name','')+' '+element.findtext('uri','')
        if a.no_markers and 'aruco' in name:world.remove(element)
        elif 'rc_vehicle' in name or 'rc_ackermann_vehicle' in name:
            pose=element.find('pose');parts=pose.text.split();parts[0]=str(a.x);parts[1]=str(a.y);parts[5]=str(a.yaw);pose.text=' '.join(parts)
    if a.output.exists():raise FileExistsError(a.output)
    tree.write(a.output,encoding='unicode',xml_declaration=True)

if __name__=='__main__':main()
