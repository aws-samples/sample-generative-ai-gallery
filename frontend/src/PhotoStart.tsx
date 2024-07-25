import React from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import './PhotoStart.css';
import bannerImage from './assets/banner-2.png';
import { useTranslation } from 'react-i18next';

const PhotoStart = () => {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();

  const handleButtonClick = () => {
    navigate('/photo/take');
  };

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
  };

  return (
    <div className="photo-start" style={{ position: 'relative' }}>
      <img src={bannerImage} alt="Bedrock Gallery Banner" className="banner-image" />
      <div className="gallery-title"><br/>{t('welcome')}
      <div className="content-container">
        <div className="start-button">
          <button onClick={handleButtonClick} className="photo-start-button">
            {t('startButton')}
          </button>
        </div>
        <div className="lang-button">
          <button onClick={() => handleLanguageChange('ko')}>한국어</button> 
          <button onClick={() => handleLanguageChange('en')}>English</button>
        </div>
      </div></div>
      <div className="copyright">
        &copy; {new Date().getFullYear()} Amazon Web Services, Inc. All rights reserved.
      </div>
    </div>
  );
};


export default PhotoStart;
