import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp,
  School,
  Timer,
  Psychology,
  Settings,
  Refresh,
  PlayArrow,
  Assessment,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { LearningAnalytics, Recommendation, LearningProgress } from '../types';
import apiService from '../services/api';
import RecommendationCard from './RecommendationCard';
import ProgressChart from './ProgressChart';
import LearningStyleIndicator from './LearningStyleIndicator';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState<LearningAnalytics | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load analytics and recommendations in parallel
      const [analyticsData, recommendationsData] = await Promise.all([
        apiService.getLearningAnalytics(30),
        apiService.getRecommendations({
          time_available: 60,
          learning_goal: 'skill_improvement',
        }),
      ]);

      setAnalytics(analyticsData);
      setRecommendations(recommendationsData);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Dashboard loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleStartLearning = async (topic?: string) => {
    try {
      // Generate personalized content for the topic
      const content = await apiService.generatePersonalizedContent(
        topic || 'general',
        'auto'
      );
      // Navigate to learning session (would be implemented with router)
      console.log('Starting learning session with content:', content);
    } catch (err) {
      console.error('Failed to start learning session:', err);
    }
  };

  const getPrimaryLearningStyle = () => {
    if (!user?.learning_style) return 'visual';
    const styles = user.learning_style;
    return Object.entries(styles).reduce((a, b) => 
      styles[a[0] as keyof typeof styles] > styles[b[0] as keyof typeof styles] ? a : b
    )[0];
  };

  const getStyleColor = (style: string) => {
    const colors = {
      visual: '#2196F3',
      auditory: '#FF9800',
      kinesthetic: '#4CAF50',
    };
    return colors[style as keyof typeof colors] || '#2196F3';
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <Grid container spacing={3}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} md={6} lg={4} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={32} />
                  <Skeleton variant="rectangular" width="100%" height={100} sx={{ mt: 2 }} />
                  <Skeleton variant="text" width="40%" height={24} sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} action={
          <Button color="inherit" size="small" onClick={loadDashboardData}>
            Retry
          </Button>
        }>
          {error}
        </Alert>
      )}

      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Avatar
            sx={{
              bgcolor: getStyleColor(getPrimaryLearningStyle()),
              width: 56,
              height: 56,
            }}
          >
            {user?.full_name?.charAt(0) || 'U'}
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1">
              Welcome back, {user?.full_name?.split(' ')[0]}!
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Ready to continue your learning journey?
            </Typography>
          </Box>
        </Box>
        <Box>
          <IconButton onClick={loadDashboardData} disabled={loading}>
            <Refresh />
          </IconButton>
          <IconButton onClick={handleMenuOpen}>
            <Settings />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleMenuClose}>Profile Settings</MenuItem>
            <MenuItem onClick={handleMenuClose}>Learning Preferences</MenuItem>
            <MenuItem onClick={handleMenuClose}>Accessibility Options</MenuItem>
          </Menu>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Learning Style Indicator */}
        <Grid item xs={12} md={6} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Psychology sx={{ mr: 1, color: getStyleColor(getPrimaryLearningStyle()) }} />
                  <Typography variant="h6">Learning Style</Typography>
                </Box>
                <LearningStyleIndicator learningStyle={user?.learning_style} />
                <Chip
                  label={`Primary: ${getPrimaryLearningStyle()}`}
                  color="primary"
                  size="small"
                  sx={{ mt: 2 }}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={6} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <TrendingUp sx={{ mr: 1, color: 'success.main' }} />
                  <Typography variant="h6">Progress Overview</Typography>
                </Box>
                {analytics && (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body2">Average Performance</Typography>
                      <Typography variant="body2" fontWeight="bold">
                        {(analytics.summary.average_performance * 100).toFixed(1)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={analytics.summary.average_performance * 100}
                      sx={{ mb: 2 }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">{analytics.summary.total_sessions}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          Sessions
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="h6">
                          {Math.round(analytics.summary.total_time_minutes)}m
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Total Time
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PlayArrow sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Quick Actions</Typography>
                </Box>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="contained"
                    startIcon={<School />}
                    onClick={() => handleStartLearning()}
                    fullWidth
                  >
                    Start Learning
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Assessment />}
                    onClick={() => handleStartLearning('assessment')}
                    fullWidth
                  >
                    Take Assessment
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<Timer />}
                    onClick={() => handleStartLearning('review')}
                    fullWidth
                  >
                    Quick Review
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Progress Chart */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Learning Progress
                </Typography>
                {analytics && (
                  <ProgressChart
                    progressData={analytics.progress_by_topic}
                    efficiencyTrends={analytics.learning_patterns.learning_efficiency_trends}
                  />
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Recommended for You
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {recommendations.slice(0, 3).map((recommendation, index) => (
                    <RecommendationCard
                      key={recommendation.content_id}
                      recommendation={recommendation}
                      onSelect={handleStartLearning}
                      compact
                    />
                  ))}
                  {recommendations.length > 3 && (
                    <Button variant="text" size="small">
                      View All Recommendations
                    </Button>
                  )}
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* AI Insights */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  AI-Powered Insights
                </Typography>
                {analytics?.recommendations && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {analytics.recommendations.map((recommendation, index) => (
                      <Alert
                        key={index}
                        severity="info"
                        variant="outlined"
                        sx={{ '& .MuiAlert-message': { width: '100%' } }}
                      >
                        {recommendation}
                      </Alert>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;