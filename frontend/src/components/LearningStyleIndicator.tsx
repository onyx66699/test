import React from 'react';
import { Box, Typography, LinearProgress, Chip } from '@mui/material';
import { Visibility, VolumeUp, TouchApp } from '@mui/icons-material';
import { LearningStyle } from '../types';

interface LearningStyleIndicatorProps {
  learningStyle?: LearningStyle;
  showLabels?: boolean;
  compact?: boolean;
}

const LearningStyleIndicator: React.FC<LearningStyleIndicatorProps> = ({
  learningStyle,
  showLabels = true,
  compact = false,
}) => {
  const defaultStyle: LearningStyle = {
    visual: 0.4,
    auditory: 0.3,
    kinesthetic: 0.3,
  };

  const style = learningStyle || defaultStyle;

  const styleConfig = [
    {
      key: 'visual' as keyof LearningStyle,
      label: 'Visual',
      icon: <Visibility />,
      color: '#2196F3',
      description: 'Learns best through visual aids, diagrams, and charts',
    },
    {
      key: 'auditory' as keyof LearningStyle,
      label: 'Auditory',
      icon: <VolumeUp />,
      color: '#FF9800',
      description: 'Learns best through listening and verbal instruction',
    },
    {
      key: 'kinesthetic' as keyof LearningStyle,
      label: 'Kinesthetic',
      icon: <TouchApp />,
      color: '#4CAF50',
      description: 'Learns best through hands-on activities and movement',
    },
  ];

  const getPrimaryStyle = () => {
    return styleConfig.reduce((prev, current) =>
      style[prev.key] > style[current.key] ? prev : current
    );
  };

  if (compact) {
    const primaryStyle = getPrimaryStyle();
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Box sx={{ color: primaryStyle.color }}>
          {primaryStyle.icon}
        </Box>
        <Box>
          <Typography variant="body2" fontWeight="bold">
            {primaryStyle.label} Learner
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {(style[primaryStyle.key] * 100).toFixed(0)}% preference
          </Typography>
        </Box>
      </Box>
    );
  }

  return (
    <Box>
      {showLabels && (
        <Typography variant="subtitle2" sx={{ mb: 2 }}>
          Your Learning Style Profile
        </Typography>
      )}
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {styleConfig.map((config) => {
          const value = style[config.key];
          const percentage = Math.round(value * 100);
          
          return (
            <Box key={config.key}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Box sx={{ color: config.color, mr: 1 }}>
                  {config.icon}
                </Box>
                <Typography variant="body2" sx={{ flexGrow: 1 }}>
                  {config.label}
                </Typography>
                <Typography variant="body2" fontWeight="bold">
                  {percentage}%
                </Typography>
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={percentage}
                sx={{
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: config.color,
                    borderRadius: 4,
                  },
                }}
              />
              
              {showLabels && (
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ mt: 0.5, display: 'block' }}
                >
                  {config.description}
                </Typography>
              )}
            </Box>
          );
        })}
      </Box>

      {showLabels && (
        <Box sx={{ mt: 2 }}>
          <Chip
            label={`Primary: ${getPrimaryStyle().label}`}
            color="primary"
            size="small"
            icon={getPrimaryStyle().icon}
          />
        </Box>
      )}
    </Box>
  );
};

export default LearningStyleIndicator;