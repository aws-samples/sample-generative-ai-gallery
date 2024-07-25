import React, { useRef, useState, useEffect } from 'react';
import Webcam from 'react-webcam';
import { useNavigate } from 'react-router-dom';
import {Buffer} from 'buffer';
import axios from 'axios';
import './PhotoTake.css';
import { useTranslation, Trans } from 'react-i18next';
import PrivacyModal from './PrivacyModal';

const PhotoTake = () => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [uploadProgress1, setUploadProgress1] = useState(0); 
  const [uploadProgress2, setUploadProgress2] = useState(100); 
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [showPrivacyModal, setShowPrivacyModal] = useState(true);
  const [agreementUserName, setAgreementUserName] = useState(null);
  const [agreementResult, setAgreementResult] = useState(false);
  
  useEffect(() => {
    // 페이지 접근 시 개인정보 동의 모달 표시
    setShowPrivacyModal(false);
  }, []);

  const handlePrivacyModalClose = () => {
    setShowPrivacyModal(false);
    navigate('/');
  };

  const handlePrivacyModalAgree = (name) => {
    console.log("handlePrivacyModal-Agree");
    setAgreementResult(true);
    setAgreementUserName(name);
    setShowPrivacyModal(false);
  };

  const handlePrivacyModalDisagree = () => {
    console.log("handlePrivacyModal-Disagree");
    setShowPrivacyModal(false);
    setAgreementResult(false);
    navigate('/'); 
  };

  const capture = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    console.log("img src= "+imageSrc);
    setCapturedImage(imageSrc);
  };

  const uploadImage = () => {
    
    setUploadProgress1(1);
    fetch(`${process.env.REACT_APP_API_ENDPOINT}/apis/images/upload`)
    .then(response => response.json())
    .then(data => {
      console.log('Fetched presigned data:', data); 
      
      console.log('uploading Image To S3');
      uploadImageToS3(data.uploadUrl, capturedImage, data.uuid);
      console.log('call Agreement API');
    })
    .catch(error => console.error('Error while uploading the image:', error));
    
  }


  const uploadImageToS3 = async (presignedUrl4Put, imageSrc, uuid) => {
    if (presignedUrl4Put) {
      try {
        const base64Data = Buffer.from(imageSrc.replace(/^data:image\/\w+;base64,/, ""), 'base64');
        const config = {
          headers: { 'Content-Type': 'image/png' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress1(percentCompleted);
          },
        };

        const response = await axios.put(presignedUrl4Put, base64Data, config);

        if (response.status === 200) {
          setUploadProgress1(100);
          console.log('Image uploaded successfully');
          navigate(`/image/${uuid}`)
        } else {
          console.error('Error uploading image');
        }
      } catch (error) {
        console.error('Error uploading image:', error);
      }
    } else {
      console.error('Presigned URL not available');
    }
  };

  const navigateToStart = () => {
    navigate('/');
  };

  const navigateToTake = () => {
    setCapturedImage(null);
    navigate('/photo/take');
  };

  return (
    <div className="container">
     <PrivacyModal
        isOpen={showPrivacyModal}
        onClose={handlePrivacyModalClose}
        onAgree={handlePrivacyModalAgree}
        onDisagree={handlePrivacyModalDisagree}
      
      />
      <div className="webcam-container">
      {(() => {
        if (!capturedImage) {
          return (<div className="webcam-container">
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/png"
              // width={480}
              // height={220}
              videoConstraints={{
                facingMode: 'user'
              }}
            />
          </div>);
        } else {
          return (<div className="webcam-container">
            <img src={capturedImage} alt="Captured Image" />
          </div>);
        }
      })()}
      </div>
      <div>
        {Math.min(uploadProgress1, uploadProgress2) > 0 && (
          <div>
            <progress value={Math.min(uploadProgress1, uploadProgress2)} max="100" />
            <span>{Math.min(uploadProgress1, uploadProgress2)}%</span>
          </div>
        )}
      </div>
      {(() => {
        if (!capturedImage) {
          return (
            <div className="capture-button"><br/><button onClick={capture}>{t('takePhoto')}</button></div>
          );
        } else {
          if (Math.min(uploadProgress1, uploadProgress2) == 100) {
            return (
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
  <div className="upload-completed-message" style={{ textAlign: 'center' }}><Trans i18nKey="uploadComplete"/></div>
  <br />
  <div className="capture-button" >
    <button onClick={navigateToStart}>{t('goBackToStart')}</button>
  </div>
</div>
            );
          } else {
            return (
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: 17 }}>
                <div className="retake-button">
                  <button onClick={navigateToTake} disabled={Math.min(uploadProgress1, uploadProgress2) > 0 && Math.min(uploadProgress1, uploadProgress2) < 100}>{t('retake')}</button>
                </div>
                <div className="capture-button"  style={{ marginLeft: '12px' }}>
                  <button onClick={uploadImage} disabled={Math.min(uploadProgress1, uploadProgress2) > 0 && Math.min(uploadProgress1, uploadProgress2) < 100}>{t('upload')}</button>
                </div>
              </div>
            );
          }
        }
      })()}
    </div>
  );
};

export default PhotoTake;
