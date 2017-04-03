from PIL import Image
import os 
import sys 
import numpy as np
import string
from PIL import Image
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

#image functions 
def resize_image(image_name):
  
  image_test = Image.open(image_name)
  img = np.array(image_test)

  if (max(img.shape[0], img.shape[1])<300):
    
    grand_image = np.zeros((300,300,3),dtype=img.dtype)
    grand_image [0:img.shape[0], 0:img.shape[1],:]=img
    
    
    result = Image.fromarray(grand_image)
    newname=string.replace(image_name, 'data', 'res')

    result.save(newname)
    return grand_image 
  else:
    im_res_save = image_test.resize([300, 300], Image.ANTIALIAS)
    newname=string.replace(image_name, 'data', 'res')
    im_res_save.save(newname) 
    
    return img

def get_product( image_name):
      result_segmentaion=string.replace(image_name, '/home/krayni/Bureau/PIXIT_SEG/API/First_API/data/', '/home/krayni/Bureau/PIXIT_SEG/res_sac/')
      print(result_segmentaion)
      result_segmentaion=string.replace(result_segmentaion, '.jpg', '_segmentation.png')
      result_segmentaion=string.replace(result_segmentaion, '.jpeg', '_segmentation.png')
      mask = np.array(Image.open(result_segmentaion)) #mask given by caffe
      find_labels=np.unique(mask)#labels
      img = np.array(Image.open(image_name))
      chk = 255.0*np.ones(img.shape,dtype=img.dtype)  
      mask = mask[:,:,np.newaxis]
      #save_sac_main
      label_sac_main=16
      label_shoes_right=9
      label_shoes_left=10
      #example_save_sac
      res = np.where(mask!=label_sac_main, chk, img)
      res=np.array(res,dtype=img.dtype) 
      
      result = Image.fromarray(res)
      interm_image=np.absolute(np.array(255.0-res,dtype=img.dtype))
      bbox_non_zero=Image.fromarray(interm_image).getbbox()
      left = min(bbox_non_zero[0], bbox_non_zero[2])
      upper = min(bbox_non_zero[1], bbox_non_zero[3])
      right = max(bbox_non_zero[0], bbox_non_zero[2])
      lower = max(bbox_non_zero[1], bbox_non_zero[3])
      s=[left, upper, right, lower]
      #new_result=result.crop(s)
      new_result=result
      result_name=string.replace(image_name, 'data', 'res')
      new_result.save( result_name)
      return find_labels


#data functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
