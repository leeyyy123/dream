-- 登录语句
mysql -uroot -p
No2023053913
use dream;

-- 建表语句
-- 创建 Users 表
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    UserName VARCHAR(50) NOT NULL UNIQUE,  
    Email VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,        
    AvatarUrl VARCHAR(500),              
    Gender ENUM('M', 'F', 'O'),        
    BirthDate DATE,
    RegisterTime DATETIME DEFAULT CURRENT_TIMESTAMP,  
    LastLogin DATETIME,
    INDEX idx_email (Email),
    INDEX idx_username (UserName)
);

-- 创建 Dreams 表
CREATE TABLE Dreams (
    DreamID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Title VARCHAR(100) NOT NULL,
    Content TEXT NOT NULL,
    DreamDate DATE NOT NULL,
    SleepQuality INT CHECK (SleepQuality >= 1 AND SleepQuality <= 5), 
    LucidityLevel INT CHECK (LucidityLevel >= 1 AND LucidityLevel <= 5),
    RecordTime DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 默认值
    IsPublic BOOLEAN DEFAULT FALSE,        -- 隐私设置
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_user_dreamdate (UserID, DreamDate),  -- 复合索引
    INDEX idx_user (UserID)
);

-- 创建 Keywords 表
CREATE TABLE Keywords (
    KeywordID INT PRIMARY KEY AUTO_INCREMENT,
    DreamID INT NOT NULL,
    KeywordText VARCHAR(50) NOT NULL,
    Category ENUM('person', 'place', 'object', 'event', 'symbol', 'other'),  -- 标准化分类
    Weight INT CHECK (Weight >= 1 AND Weight <= 3), 
    FOREIGN KEY (DreamID) REFERENCES Dreams(DreamID) ON DELETE CASCADE,
    INDEX idx_dream_category (DreamID, Category)
);

-- 创建 Images 表
CREATE TABLE Images (
    ImageID INT PRIMARY KEY AUTO_INCREMENT,
    ImageName VARCHAR(100) NOT NULL,
    OriginalName VARCHAR(100),
    MimeType VARCHAR(50) NOT NULL,
    FileSize INT,
    Width INT,
    Height INT,
    CompressedData LONGBLOB,
    CompressionRatio DECIMAL(5,2),
    CreatedTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    IsActive BOOLEAN DEFAULT TRUE
);

-- 创建 Analyses 表
CREATE TABLE Analyses (
    AnalysisID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,                   -- 关联用户
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL, 
    Result JSON, 
    Recommendation TEXT,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_user_period (UserID, StartDate, EndDate)
);

-- 创建 Emotions 表
CREATE TABLE Emotions (
    EmotionID INT PRIMARY KEY AUTO_INCREMENT,
    EmotionName VARCHAR(50) NOT NULL,
    Color VARCHAR(7) NOT NULL DEFAULT '#000000'
);

-- 创建 DreamTypes 表
CREATE TABLE DreamTypes (
    TypeID INT PRIMARY KEY AUTO_INCREMENT,
    TypeName VARCHAR(50) NOT NULL,
    Color VARCHAR(7) NOT NULL DEFAULT '#000000'
);

-- 梦境-情绪关联表
CREATE TABLE DreamEmotions (
    DreamID INT NOT NULL,
    EmotionID INT NOT NULL,
    Intensity INT CHECK (Intensity BETWEEN 1 AND 10),  -- 情绪强度
    IsPrimary BOOLEAN DEFAULT FALSE,       -- 是否主导情绪
    PRIMARY KEY (DreamID, EmotionID),
    FOREIGN KEY (DreamID) REFERENCES Dreams(DreamID) ON DELETE CASCADE,
    FOREIGN KEY (EmotionID) REFERENCES Emotions(EmotionID) ON DELETE CASCADE
);

-- 梦境-类型关联表
CREATE TABLE DreamTypesRelation (
    DreamID INT NOT NULL,
    TypeID INT NOT NULL,
    Confidence DECIMAL(3,2) DEFAULT 1.00,  -- 分类置信度
    PRIMARY KEY (DreamID, TypeID),
    FOREIGN KEY (DreamID) REFERENCES Dreams(DreamID) ON DELETE CASCADE,
    FOREIGN KEY (TypeID) REFERENCES DreamTypes(TypeID) ON DELETE CASCADE
);

-- 创建 Logs 表
CREATE TABLE Logs (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,  
    LogType ENUM('login', 'logout', 'record', 'update', 'delete', 'analysis', 'error') NOT NULL,
    ActionDescription TEXT NOT NULL,
    IP VARCHAR(45) NOT NULL,               -- 支持IPv6
    UserAgent TEXT,                        -- 浏览器信息
    AdditionalData JSON,                   -- 额外数据
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE SET NULL,
    INDEX idx_log_type (LogType),
    INDEX idx_timestamp (Timestamp),
    INDEX idx_user_logs (UserID, Timestamp)
);