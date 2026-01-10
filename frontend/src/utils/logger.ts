export const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3
} as const;

export type LogLevelType = typeof LogLevel[keyof typeof LogLevel];

export interface LogEntry {
    timestamp: Date;
    level: LogLevelType;
    message: string;
    metadata?: Record<string, any>;
}

class Logger {
    private static instance: Logger;
    private logLevel: LogLevelType = LogLevel.INFO;
    private logs: LogEntry[] = [];
    private maxLogs: number = 1000; // 最大保存的日志条数

    public static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    public setLogLevel(level: LogLevelType): void {
        this.logLevel = level;
    }

    public debug(message: string, metadata?: Record<string, any>): void {
        this.log(LogLevel.DEBUG, message, metadata);
    }

    public info(message: string, metadata?: Record<string, any>): void {
        this.log(LogLevel.INFO, message, metadata);
    }

    public warn(message: string, metadata?: Record<string, any>): void {
        this.log(LogLevel.WARN, message, metadata);
    }

    public error(message: string, metadata?: Record<string, any>): void {
        this.log(LogLevel.ERROR, message, metadata);
    }

    private log(level: LogLevelType, message: string, metadata?: Record<string, any>): void {
        if (level < this.logLevel) {
            return;
        }

        const logEntry: LogEntry = {
            timestamp: new Date(),
            level,
            message,
            metadata
        };

        console.log(this.formatLog(logEntry));

        // 存储到内存中
        this.logs.push(logEntry);

        // 如果超过最大数量，移除最早的日志
        if (this.logs.length > this.maxLogs) {
            this.logs.shift();
        }

        // 同时保存到localStorage（可选）
        this.saveToStorage();
    }

    private formatLog(entry: LogEntry): string {
        const levelNames = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
        const timestamp = entry.timestamp.toISOString();
        const levelIndex = Object.values(LogLevel).indexOf(entry.level);
        const levelName = levelNames[levelIndex];
        const metaStr = entry.metadata ? ` | Metadata: ${JSON.stringify(entry.metadata)}` : '';

        return `[${timestamp}] ${levelName}: ${entry.message}${metaStr}`;
    }

    private saveToStorage(): void {
        try {
            localStorage.setItem('app_logs', JSON.stringify(this.logs.map(log => ({
                ...log,
                timestamp: log.timestamp.toISOString()
            }))));
        } catch (error) {
            console.warn('Failed to save logs to localStorage:', error);
        }
    }

    public getLogs(): LogEntry[] {
        return [...this.logs]; // 返回副本，避免外部修改
    }

    public clearLogs(): void {
        this.logs = [];
        localStorage.removeItem('app_logs');
    }

    public exportLogs(): string {
        return JSON.stringify(this.logs.map(log => ({
            ...log,
            timestamp: log.timestamp.toISOString()
        })), null, 2);
    }
}

export const logger = Logger.getInstance();

// 便捷函数
export const logDebug = (message: string, metadata?: Record<string, any>) => logger.debug(message, metadata);
export const logInfo = (message: string, metadata?: Record<string, any>) => logger.info(message, metadata);
export const logWarn = (message: string, metadata?: Record<string, any>) => logger.warn(message, metadata);
export const logError = (message: string, metadata?: Record<string, any>) => logger.error(message, metadata);