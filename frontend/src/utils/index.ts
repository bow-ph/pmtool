export const cn = (...classes: (string | boolean | undefined | null | { [key: string]: boolean })[]): string => {
  return classes
    .filter(Boolean)
    .map((cls) => {
      if (typeof cls === 'object' && cls !== null) {
        return Object.entries(cls)
          .filter(([, value]) => value)
          .map(([key]) => key)
          .join(' ');
      }
      return cls;
    })
    .join(' ');
};
