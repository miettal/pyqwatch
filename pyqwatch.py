#!/usr/bin/env python
import socket
import sys
import base64
import netifaces
import netaddr

def fetch_image(host, user, password, callback) :
  s = socket.create_connection((str(host), 80), 60)
  fh = s.makefile()
  
  # Request
  fh.write(('GET /snapshot.cgi HTTP/1.1\r\n'
  +'Host: ' + host+':80\r\n'
  +'Connection: keep-alive\r\n'
  +'Authorization: Basic ' + base64.b64encode(user+':'+password) + '\r\n\r\n'
  ))
  fh.flush()
  
  # Response
  line = fh.readline()
  while line.strip() != '': 
      parts = line.split(':')
      if len(parts) > 1 and parts[0].lower() == 'content-type':
          # Extract boundary string from content-type
          content_type = parts[1].strip()
          boundary = content_type.split(';')[1].split('=')[1].strip('"')
      line = fh.readline()
  
  if not boundary:
      raise Exception("Can't find content-type")
  
  while True :
    # Find boundary
    while line.strip() != "--" + boundary:
        line = fh.readline()
    
    # Get!!!!!!!!!!!!!!!!!!!
    while line.strip() != '': 
        parts = line.split(':')
        if len(parts) > 1 and parts[0].lower() == 'content-length':
            # Grab chunk length
            length = int(parts[1].strip())
        line = fh.readline()
    
    # Callback
    image = fh.read(length)
    callback(image)
  
  s.close()

def search(interface, port, user, password) :
  local_host_addr = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']

  broadcast = netaddr.ip.IPNetwork(local_host_addr+'/24').broadcast
  network = netaddr.ip.IPNetwork(local_host_addr+'/24').network
  for host in netaddr.ip.IPNetwork(local_host_addr+'/24') :
    if host == broadcast or host == network :
      continue

    try :
      s = socket.create_connection((str(host), port), 0.2)
      fh = s.makefile()
      
      # Request
      fh.write(('GET /snapshot.cgi HTTP/1.1\r\n'
      +'Host: ' + str(host) + ':' + str(port) + '\r\n'
      +'Connection: keep-alive\r\n'
      +'Authorization: Basic ' + base64.b64encode(user+':'+password) + '\r\n\r\n'
      ))
      fh.flush()
      
      # Response
      line = fh.readline()
      if line.strip() != "HTTP/1.1 200 OK" :
        continue

      s.close()
      return str(host)
    except (socket.timeout, socket.error) :
      continue
