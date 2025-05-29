import React from 'react';
import MuiCard from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import { SxProps } from '@mui/material/styles';

interface CardProps {
  title?: string;
  description?: string;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  onClick?: React.MouseEventHandler<HTMLDivElement>;
  sx?: SxProps;
}

/**
 * Accessible Card component:
 * - Focusable and keyboard-activatable if clickable
 * - Uses role="button" and aria-label for screen readers
 * - Shows visible focus ring when focused
 */
const Card: React.FC<CardProps> = ({ title, description, children, style, onClick, sx }) => {
  const isClickable = Boolean(onClick);
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (!isClickable) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.(e as any);
    }
  };
  return (
    <MuiCard
      elevation={2}
      sx={{
        borderRadius: 2,
        outline: 'none',
        cursor: isClickable ? 'pointer' : undefined,
        transition: 'box-shadow 0.2s, background 0.2s',
        '&:hover': isClickable ? { boxShadow: 6, background: '#f3f6fa' } : undefined,
        '&:focus': isClickable ? { boxShadow: '0 0 0 3px #1976d2', background: '#e3eefd' } : undefined,
        ...style,
        ...sx,
      }}
      onClick={onClick}
      tabIndex={isClickable ? 0 : undefined}
      role={isClickable ? 'button' : undefined}
      aria-label={title ? title : undefined}
      onKeyDown={handleKeyDown}
    >
      <CardContent>
        {title && <Typography variant="h3" gutterBottom>{title}</Typography>}
        {description && <Typography variant="body2" color="text.secondary" gutterBottom>{description}</Typography>}
        {children}
      </CardContent>
    </MuiCard>
  );
};

export default Card; 