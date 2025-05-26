import React from 'react';
import TextField, { TextFieldProps } from '@mui/material/TextField';

const Input: React.FC<TextFieldProps> = (props) => {
  return <TextField variant="outlined" margin="normal" fullWidth {...props} />;
};

export default Input; 