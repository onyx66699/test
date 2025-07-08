import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Schedule,
  TrendingUp,
  Info,
  Star,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { Recommendation } from '../types';

interface RecommendationCardProps {
  recommendation: Recommendation;
  onSelect: (contentId: number) => void;
  compact?: boolean;
  showDetails?: boolean;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({
  recommendation,
  onSelect,
  compact = false,
  showDetails = true,
}) => {
  const getContentTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      video: '#FF5722',
      interactive: '#4CAF50',
      quiz: '#2196F3',
      reading: '#9C27B0',
      audio: '#FF9800',
      exercise: '#00BCD4',
    };
    return colors[type] || '#757575';
  };

  const getContentTypeIcon = (type: string) => {
    // In a real app, you'd have proper icons for each type
    return type.charAt(0).toUpperCase();
  };

  const getDifficultyLabel = (difficulty: number) => {
    if (difficulty < 0.3) return 'Beginner';
    if (difficulty < 0.7) return 'Intermediate';
    return 'Advanced';
  };

  const getDifficultyColor = (difficulty: number) => {
    if (difficulty < 0.3) return 'success';
    if (difficulty < 0.7) return 'warning';
    return 'error';
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  if (compact) {
    return (
      <motion.div
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ duration: 0.2 }}
      >
        <Card
          sx={{
            cursor: 'pointer',
            '&:hover': {
              boxShadow: 3,
            },
          }}
          onClick={() => onSelect(recommendation.content_id)}
        >
          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 1 }}>
              <Box
                sx={{
                  width: 32,
                  height: 32,
                  borderRadius: 1,
                  backgroundColor: getContentTypeColor(recommendation.content_preview.type),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '0.875rem',
                  fontWeight: 'bold',
                  flexShrink: 0,
                }}
              >
                {getContentTypeIcon(recommendation.content_preview.type)}
              </Box>
              
              <Box sx={{ flexGrow: 1, minWidth: 0 }}>
                <Typography
                  variant="body2"
                  fontWeight="bold"
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {recommendation.content_preview.title}
                </Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                  <Chip
                    label={getDifficultyLabel(recommendation.content_preview.difficulty)}
                    size="small"
                    color={getDifficultyColor(recommendation.content_preview.difficulty) as any}
                    variant="outlined"
                  />
                  
                  <Typography variant="caption" color="text.secondary">
                    {formatDuration(recommendation.content_preview.duration)}
                  </Typography>
                </Box>
              </Box>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Star sx={{ fontSize: 16, color: 'warning.main' }} />
                <Typography variant="caption" fontWeight="bold">
                  {(recommendation.confidence_score * 100).toFixed(0)}%
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          '&:hover': {
            boxShadow: 4,
          },
        }}
      >
        <CardContent sx={{ flexGrow: 1 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                backgroundColor: getContentTypeColor(recommendation.content_preview.type),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '1.25rem',
                fontWeight: 'bold',
              }}
            >
              {getContentTypeIcon(recommendation.content_preview.type)}
            </Box>
            
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" component="h3" sx={{ mb: 1 }}>
                {recommendation.content_preview.title}
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label={recommendation.content_preview.type}
                  size="small"
                  sx={{
                    backgroundColor: getContentTypeColor(recommendation.content_preview.type),
                    color: 'white',
                  }}
                />
                <Chip
                  label={getDifficultyLabel(recommendation.content_preview.difficulty)}
                  size="small"
                  color={getDifficultyColor(recommendation.content_preview.difficulty) as any}
                />
              </Box>
            </Box>
          </Box>

          {/* Confidence Score */}
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                AI Confidence
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {(recommendation.confidence_score * 100).toFixed(0)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={recommendation.confidence_score * 100}
              sx={{ height: 6, borderRadius: 3 }}
            />
          </Box>

          {/* Details */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Schedule sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="body2" color="text.secondary">
                {formatDuration(recommendation.content_preview.duration)}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <TrendingUp sx={{ fontSize: 16, color: 'success.main' }} />
              <Typography variant="body2" color="success.main" fontWeight="bold">
                {(recommendation.estimated_benefit * 100).toFixed(0)}% benefit
              </Typography>
            </Box>
          </Box>

          {/* Reasoning */}
          {showDetails && recommendation.reasoning && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Why recommended:</strong> {recommendation.reasoning.primary_reason}
              </Typography>
              {recommendation.reasoning.supporting_factors && 
               recommendation.reasoning.supporting_factors.length > 0 && (
                <Box sx={{ mt: 1 }}>
                  {recommendation.reasoning.supporting_factors.map((factor: string, index: number) => (
                    <Typography
                      key={index}
                      variant="caption"
                      color="text.secondary"
                      sx={{ display: 'block', ml: 1 }}
                    >
                      • {factor}
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </CardContent>

        <CardActions sx={{ p: 2, pt: 0 }}>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={() => onSelect(recommendation.content_id)}
            fullWidth
          >
            Start Learning
          </Button>
          
          {showDetails && (
            <Tooltip title="More information">
              <IconButton size="small">
                <Info />
              </IconButton>
            </Tooltip>
          )}
        </CardActions>
      </Card>
    </motion.div>
  );
};

export default RecommendationCard;