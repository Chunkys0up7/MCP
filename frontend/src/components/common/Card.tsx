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

const Card: React.FC<CardProps> = ({ title, description, children, style, onClick, sx }) => (
  <MuiCard elevation={2} sx={{ borderRadius: 2, ...style, ...sx }} onClick={onClick} tabIndex={onClick ? 0 : undefined} role={onClick ? 'button' : undefined}>
    <CardContent>
      {title && <Typography variant="h3" gutterBottom>{title}</Typography>}
      {description && <Typography variant="body2" color="text.secondary" gutterBottom>{description}</Typography>}
      {children}
    </CardContent>
  </MuiCard>
);

export default Card; 