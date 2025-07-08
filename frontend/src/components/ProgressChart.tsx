import React, { useState } from 'react';
import {
  Box,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { LearningProgress } from '../types';

interface ProgressChartProps {
  progressData: Record<string, LearningProgress>;
  efficiencyTrends?: any[];
}

type ChartType = 'progress' | 'efficiency' | 'distribution';

const ProgressChart: React.FC<ProgressChartProps> = ({
  progressData,
  efficiencyTrends = [],
}) => {
  const theme = useTheme();
  const [chartType, setChartType] = useState<ChartType>('progress');

  const handleChartTypeChange = (
    event: React.MouseEvent<HTMLElement>,
    newType: ChartType,
  ) => {
    if (newType !== null) {
      setChartType(newType);
    }
  };

  // Prepare data for different chart types
  const progressChartData = Object.entries(progressData).map(([topic, progress]) => ({
    topic: topic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    skillLevel: Math.round(progress.skill_level * 100),
    completionRate: Math.round(progress.completion_rate * 100),
    timeSpent: progress.time_spent,
  }));

  const efficiencyChartData = efficiencyTrends.map((trend, index) => ({
    session: `Session ${index + 1}`,
    efficiency: Math.round(trend.efficiency * 100),
    timestamp: trend.timestamp,
  }));

  const distributionData = [
    {
      name: 'Beginner',
      value: progressChartData.filter(item => item.skillLevel < 40).length,
      color: '#4CAF50',
    },
    {
      name: 'Intermediate',
      value: progressChartData.filter(item => item.skillLevel >= 40 && item.skillLevel < 70).length,
      color: '#FF9800',
    },
    {
      name: 'Advanced',
      value: progressChartData.filter(item => item.skillLevel >= 70).length,
      color: '#F44336',
    },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'background.paper',
            border: 1,
            borderColor: 'divider',
            borderRadius: 1,
            p: 1,
            boxShadow: 2,
          }}
        >
          <Typography variant="body2" fontWeight="bold">
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {entry.value}
              {entry.name.includes('Level') || entry.name.includes('Rate') || entry.name.includes('efficiency') ? '%' : ''}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  const renderProgressChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={progressChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis
          dataKey="topic"
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <Tooltip content={<CustomTooltip />} />
        <Bar
          dataKey="skillLevel"
          name="Skill Level"
          fill={theme.palette.primary.main}
          radius={[4, 4, 0, 0]}
        />
        <Bar
          dataKey="completionRate"
          name="Completion Rate"
          fill={theme.palette.secondary.main}
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderEfficiencyChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={efficiencyChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
        <XAxis
          dataKey="session"
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          stroke={theme.palette.text.secondary}
        />
        <Tooltip content={<CustomTooltip />} />
        <Line
          type="monotone"
          dataKey="efficiency"
          name="Learning Efficiency"
          stroke={theme.palette.success.main}
          strokeWidth={3}
          dot={{ fill: theme.palette.success.main, strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  const renderDistributionChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={distributionData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={5}
          dataKey="value"
          label={({ name, value, percent }) => 
            value > 0 ? `${name}: ${(percent * 100).toFixed(0)}%` : ''
          }
        >
          {distributionData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <Box
                  sx={{
                    backgroundColor: 'background.paper',
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    p: 1,
                    boxShadow: 2,
                  }}
                >
                  <Typography variant="body2" fontWeight="bold">
                    {data.name} Level
                  </Typography>
                  <Typography variant="body2">
                    Topics: {data.value}
                  </Typography>
                </Box>
              );
            }
            return null;
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );

  const renderChart = () => {
    switch (chartType) {
      case 'progress':
        return renderProgressChart();
      case 'efficiency':
        return renderEfficiencyChart();
      case 'distribution':
        return renderDistributionChart();
      default:
        return renderProgressChart();
    }
  };

  const getChartDescription = () => {
    switch (chartType) {
      case 'progress':
        return 'Skill level and completion rate by topic';
      case 'efficiency':
        return 'Learning efficiency trends over time';
      case 'distribution':
        return 'Distribution of topics by skill level';
      default:
        return '';
    }
  };

  if (!progressData || Object.keys(progressData).length === 0) {
    return (
      <Box
        sx={{
          height: 300,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'text.secondary',
        }}
      >
        <Typography variant="body1">
          No progress data available yet. Start learning to see your progress!
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          {getChartDescription()}
        </Typography>
        
        <ToggleButtonGroup
          value={chartType}
          exclusive
          onChange={handleChartTypeChange}
          size="small"
        >
          <ToggleButton value="progress">
            Progress
          </ToggleButton>
          <ToggleButton value="efficiency">
            Efficiency
          </ToggleButton>
          <ToggleButton value="distribution">
            Distribution
          </ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {renderChart()}

      {/* Summary Stats */}
      <Box sx={{ display: 'flex', justifyContent: 'space-around', mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="primary">
            {Object.keys(progressData).length}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Topics
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="success.main">
            {progressChartData.length > 0 
              ? Math.round(progressChartData.reduce((sum, item) => sum + item.skillLevel, 0) / progressChartData.length)
              : 0}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Avg. Skill
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="warning.main">
            {progressChartData.length > 0
              ? Math.round(progressChartData.reduce((sum, item) => sum + item.completionRate, 0) / progressChartData.length)
              : 0}%
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Avg. Completion
          </Typography>
        </Box>
        
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="info.main">
            {progressChartData.reduce((sum, item) => sum + item.timeSpent, 0)}h
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Total Time
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default ProgressChart;