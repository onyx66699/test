import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Link,
  InputAdornment,
  IconButton,
  Divider,
  FormControlLabel,
  Checkbox,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Lock,
  Email,
  Psychology,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { RegisterData, LearningStyle, NeurodivergentAccommodations } from '../types';
import LearningStyleIndicator from './LearningStyleIndicator';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ onSwitchToLogin }) => {
  const { register } = useAuth();
  const [activeStep, setActiveStep] = useState(0);
  const [userData, setUserData] = useState<RegisterData>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    learning_style: {
      visual: 0.4,
      auditory: 0.3,
      kinesthetic: 0.3,
    },
    neurodivergent_accommodations: {
      needs_breaks: false,
      prefers_structure: true,
      sensitive_to_distractions: false,
      needs_extra_time: false,
      benefits_from_repetition: false,
      prefers_clear_instructions: true,
    },
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const steps = ['Basic Information', 'Learning Preferences', 'Accessibility Options'];

  const handleChange = (field: keyof RegisterData) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setUserData(prev => ({
      ...prev,
      [field]: event.target.value,
    }));
    if (error) setError(null);
  };

  const handleLearningStyleChange = (style: keyof LearningStyle, value: number) => {
    setUserData(prev => ({
      ...prev,
      learning_style: {
        ...prev.learning_style!,
        [style]: value,
      },
    }));
  };

  const handleAccommodationChange = (accommodation: keyof NeurodivergentAccommodations) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setUserData(prev => ({
      ...prev,
      neurodivergent_accommodations: {
        ...prev.neurodivergent_accommodations!,
        [accommodation]: event.target.checked,
      },
    }));
  };

  const handleNext = () => {
    if (activeStep === 0) {
      // Validate basic information
      if (!userData.username || !userData.email || !userData.password || !userData.full_name) {
        setError('Please fill in all required fields');
        return;
      }
      if (userData.password.length < 6) {
        setError('Password must be at least 6 characters long');
        return;
      }
    }
    
    setError(null);
    setActiveStep(prev => prev + 1);
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      await register(userData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const renderBasicInformation = () => (
    <Box>
      <TextField
        fullWidth
        label="Full Name"
        value={userData.full_name}
        onChange={handleChange('full_name')}
        margin="normal"
        required
        autoComplete="name"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Person color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        fullWidth
        label="Username"
        value={userData.username}
        onChange={handleChange('username')}
        margin="normal"
        required
        autoComplete="username"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Person color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        fullWidth
        label="Email"
        type="email"
        value={userData.email}
        onChange={handleChange('email')}
        margin="normal"
        required
        autoComplete="email"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Email color="action" />
            </InputAdornment>
          ),
        }}
      />

      <TextField
        fullWidth
        label="Password"
        type={showPassword ? 'text' : 'password'}
        value={userData.password}
        onChange={handleChange('password')}
        margin="normal"
        required
        autoComplete="new-password"
        helperText="Minimum 6 characters"
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <Lock color="action" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                onClick={togglePasswordVisibility}
                edge="end"
                aria-label="toggle password visibility"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />
    </Box>
  );

  const renderLearningPreferences = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Learning Style Assessment
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Help us understand how you learn best. You can adjust these preferences later.
      </Typography>

      <LearningStyleIndicator learningStyle={userData.learning_style} />

      <Box sx={{ mt: 3 }}>
        <Typography variant="subtitle2" gutterBottom>
          Adjust Your Learning Style Preferences:
        </Typography>
        
        {Object.entries(userData.learning_style!).map(([style, value]) => (
          <Box key={style} sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              {style.charAt(0).toUpperCase() + style.slice(1)}: {Math.round(value * 100)}%
            </Typography>
            <input
              type="range"
              min="0"
              max="100"
              value={value * 100}
              onChange={(e) => handleLearningStyleChange(
                style as keyof LearningStyle,
                parseInt(e.target.value) / 100
              )}
              style={{ width: '100%' }}
            />
          </Box>
        ))}
      </Box>
    </Box>
  );

  const renderAccessibilityOptions = () => (
    <Box>
      <Typography variant="h6" gutterBottom>
        Accessibility & Learning Support
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Select any accommodations that would help improve your learning experience.
      </Typography>

      {Object.entries(userData.neurodivergent_accommodations!).map(([key, value]) => (
        <FormControlLabel
          key={key}
          control={
            <Checkbox
              checked={value}
              onChange={handleAccommodationChange(key as keyof NeurodivergentAccommodations)}
            />
          }
          label={
            <Box>
              <Typography variant="body2">
                {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {getAccommodationDescription(key)}
              </Typography>
            </Box>
          }
          sx={{ display: 'block', mb: 1 }}
        />
      ))}
    </Box>
  );

  const getAccommodationDescription = (key: string) => {
    const descriptions: Record<string, string> = {
      needs_breaks: 'Regular break reminders during learning sessions',
      prefers_structure: 'Clear structure and organization in content',
      sensitive_to_distractions: 'Minimized visual and audio distractions',
      needs_extra_time: 'Extended time for activities and assessments',
      benefits_from_repetition: 'Multiple exposures to the same content',
      prefers_clear_instructions: 'Step-by-step, explicit instructions',
    };
    return descriptions[key] || '';
  };

  const renderStepContent = () => {
    switch (activeStep) {
      case 0:
        return renderBasicInformation();
      case 1:
        return renderLearningPreferences();
      case 2:
        return renderAccessibilityOptions();
      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
        <CardContent sx={{ p: 4 }}>
          {/* Header */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box
              sx={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 64,
                height: 64,
                borderRadius: '50%',
                backgroundColor: 'primary.main',
                color: 'white',
                mb: 2,
              }}
            >
              <Psychology sx={{ fontSize: 32 }} />
            </Box>
            <Typography variant="h4" component="h1" gutterBottom>
              Join Our Platform
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Create your personalized adaptive learning experience
            </Typography>
          </Box>

          {/* Stepper */}
          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {/* Error Alert */}
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}

          {/* Step Content */}
          <Box sx={{ mb: 4 }}>
            {renderStepContent()}
          </Box>

          {/* Navigation Buttons */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              onClick={activeStep === 0 ? onSwitchToLogin : handleBack}
              disabled={loading}
            >
              {activeStep === 0 ? 'Back to Login' : 'Back'}
            </Button>

            <Button
              variant="contained"
              onClick={activeStep === steps.length - 1 ? handleSubmit : handleNext}
              disabled={loading}
            >
              {loading ? 'Creating Account...' : activeStep === steps.length - 1 ? 'Create Account' : 'Next'}
            </Button>
          </Box>

          {/* Login Link */}
          {activeStep === 0 && (
            <>
              <Divider sx={{ my: 3 }}>
                <Typography variant="body2" color="text.secondary">
                  or
                </Typography>
              </Divider>

              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Already have an account?{' '}
                  <Link
                    component="button"
                    type="button"
                    onClick={onSwitchToLogin}
                    sx={{ textDecoration: 'none' }}
                  >
                    Sign in here
                  </Link>
                </Typography>
              </Box>
            </>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default RegisterForm;