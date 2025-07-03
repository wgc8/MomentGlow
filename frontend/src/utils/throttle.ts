// utils/throttle.ts
type Timer = NodeJS.Timeout | number | null;

interface ThrottleOptions {
  leading?: boolean; // 是否立即执行第一次
  trailing?: boolean; // 是否在延迟结束后执行最后一次
}

export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number,
  options: ThrottleOptions = {}
): (...args: Parameters<T>) => void {
  const { leading = true, trailing = true } = options;
  let timer: Timer = null;
  let lastArgs: Parameters<T> | null = null;
  
  return function(this: ThisParameterType<T>, ...args: Parameters<T>) {
    lastArgs = args;
    
    if (!timer) {
      if (leading) {
        func.apply(this, args);
      }
      
      timer = setTimeout(() => {
        if (trailing && lastArgs) {
          func.apply(this, lastArgs);
        }
        timer = null;
        lastArgs = null;
      }, delay);
    }
  };
}