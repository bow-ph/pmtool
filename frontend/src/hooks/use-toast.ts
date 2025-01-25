import { toast as hotToast } from 'react-hot-toast';

export const toast = {
  default: (message: string) => hotToast(message),
  success: (message: string) => hotToast.success(message),
  error: (message: string) => hotToast.error(message),
  info: (message: string) => hotToast(message, { icon: '🔔' })
};

export default toast;
