ALTER TABLE [dbo].[OEE] DROP CONSTRAINT [DF__OEE__TimeStamp__7A672E12]
GO
/****** Object:  Table [dbo].[Shifts]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Shifts]') AND type in (N'U'))
DROP TABLE [dbo].[Shifts]
GO
/****** Object:  Table [dbo].[ShiftPlannedDownTime]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ShiftPlannedDownTime]') AND type in (N'U'))
DROP TABLE [dbo].[ShiftPlannedDownTime]
GO
/****** Object:  Table [dbo].[Products]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Products]') AND type in (N'U'))
DROP TABLE [dbo].[Products]
GO
/****** Object:  Table [dbo].[ProductQuality]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ProductQuality]') AND type in (N'U'))
DROP TABLE [dbo].[ProductQuality]
GO
/****** Object:  Table [dbo].[OEE]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[OEE]') AND type in (N'U'))
DROP TABLE [dbo].[OEE]
GO
/****** Object:  Table [dbo].[Locations]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Locations]') AND type in (N'U'))
DROP TABLE [dbo].[Locations]
GO
/****** Object:  Table [dbo].[AssetTags]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AssetTags]') AND type in (N'U'))
DROP TABLE [dbo].[AssetTags]
GO
/****** Object:  Table [dbo].[Assets]    Script Date: 7/5/2022 5:53:28 PM ******/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Assets]') AND type in (N'U'))
DROP TABLE [dbo].[Assets]
GO
/****** Object:  Table [dbo].[Assets]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Assets](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[PlantId] [int] NOT NULL,
	[AssetName] [nvarchar](100) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[AssetTags]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[AssetTags](
	[AssetId] [int] NOT NULL,
	[NodeId] [nvarchar](200) NOT NULL,
	[StatusTagName] [nvarchar](100) NOT NULL,
	[UptimeTagValues] [nvarchar](100) NOT NULL,
	[DowntimeTagValues] [nvarchar](100) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Locations]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Locations](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[PlantName] [nvarchar](100) NOT NULL,
	[PlantLocation] [nvarchar](100) NOT NULL,
	[UtcOffsetInHours] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[OEE]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[OEE](
	[PlantId] [int] NOT NULL,
	[AssetId] [int] NOT NULL,
	[ShiftId] [int] NOT NULL,
	[ProductId] [int] NOT NULL,
	[TotalUnits] [float] NOT NULL,
	[GoodUnits] [float] NOT NULL,
	[BadUnits] [float] NOT NULL,
	[PlannedProductionTime] [float] NOT NULL,
	[DownTime] [float] NOT NULL,
	[RunTime] [float] NOT NULL,
	[Availability] [float] NOT NULL,
	[Performance] [float] NOT NULL,
	[Quality] [float] NOT NULL,
	[OEE] [float] NOT NULL,
	[TimeStamp] [datetime2](7) NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ProductQuality]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ProductQuality](
	[WorkOrder] [nvarchar](100) NOT NULL,
	[ShiftId] [int] NOT NULL,
	[AssetId] [int] NOT NULL,
	[ProductId] [int] NOT NULL,
	[QuantityIn] [int] NOT NULL,
	[QuantityOut] [int] NOT NULL,
	[QuantityScraped] [int] NOT NULL,
	[CreatedTimeStamp] [datetime] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Products]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Products](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[ProductName] [nvarchar](100) NOT NULL,
	[IdealProductionUnitsPerMinute] [int] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[ShiftPlannedDownTime]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[ShiftPlannedDownTime](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[ShiftId] [int] NOT NULL,
	[PlannedDownTimeReason] [nvarchar](100) NOT NULL,
	[PlannedDownTimeInMinutes] [int] NOT NULL,
	[CreatedTimeStamp] [datetime] NOT NULL
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[Shifts]    Script Date: 7/5/2022 5:53:28 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[Shifts](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[PlantId] [int] NOT NULL,
	[ShiftName] [nvarchar](50) NOT NULL,
	[ShiftStartTime] [time](7) NOT NULL,
	[ShiftEndTime] [time](7) NOT NULL
) ON [PRIMARY]
GO
SET IDENTITY_INSERT [dbo].[Assets] ON 
GO
INSERT [dbo].[Assets] ([Id], [PlantId], [AssetName]) VALUES (1, 1, N'Line1')
GO
INSERT [dbo].[Assets] ([Id], [PlantId], [AssetName]) VALUES (2, 1, N'Line2')
GO
INSERT [dbo].[Assets] ([Id], [PlantId], [AssetName]) VALUES (3, 2, N'Line3')
GO
INSERT [dbo].[Assets] ([Id], [PlantId], [AssetName]) VALUES (4, 2, N'Line4')
GO
SET IDENTITY_INSERT [dbo].[Assets] OFF
GO
INSERT [dbo].[AssetTags] ([AssetId], [NodeId], [StatusTagName], [UptimeTagValues], [DowntimeTagValues]) VALUES (1, N'opc.tcp://10.0.0.4:49320_b475f0d02c5268c4e3942a507df64b61abe193e9', N'nsu=KEPServerEX;s=Simulator.Line1.Status', N'1,2', N'3,4')
GO
INSERT [dbo].[AssetTags] ([AssetId], [NodeId], [StatusTagName], [UptimeTagValues], [DowntimeTagValues]) VALUES (2, N'opc.tcp://10.0.0.4:49320_b475f0d02c5268c4e3942a507df64b61abe193e9', N'nsu=KEPServerEX;s=Simulator.Line2.Status', N'1,2', N'3,4')
GO
INSERT [dbo].[AssetTags] ([AssetId], [NodeId], [StatusTagName], [UptimeTagValues], [DowntimeTagValues]) VALUES (3, N'opc.tcp://10.0.0.4:49320_b475f0d02c5268c4e3942a507df64b61abe193e9', N'nsu=KEPServerEX;s=Simulator.Line3.Status', N'1,2', N'3,4')
GO
INSERT [dbo].[AssetTags] ([AssetId], [NodeId], [StatusTagName], [UptimeTagValues], [DowntimeTagValues]) VALUES (4, N'opc.tcp://10.0.0.4:49320_b475f0d02c5268c4e3942a507df64b61abe193e9', N'nsu=KEPServerEX;s=Simulator.Line4.Status', N'1,2', N'3,4')
GO
SET IDENTITY_INSERT [dbo].[Locations] ON 
GO
INSERT [dbo].[Locations] ([Id], [PlantName], [PlantLocation], [UtcOffsetInHours]) VALUES (1, N'Plant-1', N'North America', -7)
GO
INSERT [dbo].[Locations] ([Id], [PlantName], [PlantLocation], [UtcOffsetInHours]) VALUES (2, N'Plant-2', N'South America', -5)
GO
SET IDENTITY_INSERT [dbo].[Locations] OFF
GO
INSERT [dbo].[ProductQuality] ([WorkOrder], [ShiftId], [AssetId], [ProductId], [QuantityIn], [QuantityOut], [QuantityScraped], [CreatedTimeStamp]) VALUES (N'WB001', 1, 1, 1, 400, 375, 25, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ProductQuality] ([WorkOrder], [ShiftId], [AssetId], [ProductId], [QuantityIn], [QuantityOut], [QuantityScraped], [CreatedTimeStamp]) VALUES (N'WB002', 2, 2, 2, 800, 770, 30, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ProductQuality] ([WorkOrder], [ShiftId], [AssetId], [ProductId], [QuantityIn], [QuantityOut], [QuantityScraped], [CreatedTimeStamp]) VALUES (N'WB003', 3, 3, 3, 1185, 1180, 5, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ProductQuality] ([WorkOrder], [ShiftId], [AssetId], [ProductId], [QuantityIn], [QuantityOut], [QuantityScraped], [CreatedTimeStamp]) VALUES (N'WB004', 1, 4, 1, 400, 380, 20, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ProductQuality] ([WorkOrder], [ShiftId], [AssetId], [ProductId], [QuantityIn], [QuantityOut], [QuantityScraped], [CreatedTimeStamp]) VALUES (N'WB005', 2, 4, 3, 1180, 1175, 5, CAST(N'2022-07-01T00:00:00.000' AS DateTime))
GO
SET IDENTITY_INSERT [dbo].[Products] ON 
GO
INSERT [dbo].[Products] ([Id], [ProductName], [IdealProductionUnitsPerMinute]) VALUES (1, N'Product-1', 1)
GO
INSERT [dbo].[Products] ([Id], [ProductName], [IdealProductionUnitsPerMinute]) VALUES (2, N'Product-2', 2)
GO
INSERT [dbo].[Products] ([Id], [ProductName], [IdealProductionUnitsPerMinute]) VALUES (3, N'Product-3', 3)
GO
SET IDENTITY_INSERT [dbo].[Products] OFF
GO
SET IDENTITY_INSERT [dbo].[ShiftPlannedDownTime] ON 
GO
INSERT [dbo].[ShiftPlannedDownTime] ([Id], [ShiftId], [PlannedDownTimeReason], [PlannedDownTimeInMinutes], [CreatedTimeStamp]) VALUES (1, 1, N'Breaks', 50, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ShiftPlannedDownTime] ([Id], [ShiftId], [PlannedDownTimeReason], [PlannedDownTimeInMinutes], [CreatedTimeStamp]) VALUES (2, 2, N'Breaks', 50, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ShiftPlannedDownTime] ([Id], [ShiftId], [PlannedDownTimeReason], [PlannedDownTimeInMinutes], [CreatedTimeStamp]) VALUES (3, 2, N'Other', 15, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ShiftPlannedDownTime] ([Id], [ShiftId], [PlannedDownTimeReason], [PlannedDownTimeInMinutes], [CreatedTimeStamp]) VALUES (4, 3, N'Breaks', 50, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
INSERT [dbo].[ShiftPlannedDownTime] ([Id], [ShiftId], [PlannedDownTimeReason], [PlannedDownTimeInMinutes], [CreatedTimeStamp]) VALUES (5, 3, N'Changeover', 10, CAST(N'2022-06-30T00:00:00.000' AS DateTime))
GO
SET IDENTITY_INSERT [dbo].[ShiftPlannedDownTime] OFF
GO
SET IDENTITY_INSERT [dbo].[Shifts] ON 
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (1, 1, N'First', CAST(N'00:00:00' AS Time), CAST(N'07:59:59' AS Time))
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (2, 1, N'Second', CAST(N'08:00:00' AS Time), CAST(N'15:59:59' AS Time))
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (3, 1, N'Third', CAST(N'16:00:00' AS Time), CAST(N'23:59:59' AS Time))
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (4, 2, N'First', CAST(N'00:00:00' AS Time), CAST(N'07:59:59' AS Time))
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (5, 2, N'Second', CAST(N'08:00:00' AS Time), CAST(N'15:59:59' AS Time))
GO
INSERT [dbo].[Shifts] ([Id], [PlantId], [ShiftName], [ShiftStartTime], [ShiftEndTime]) VALUES (6, 2, N'Third', CAST(N'16:00:00' AS Time), CAST(N'23:59:59' AS Time))
GO
SET IDENTITY_INSERT [dbo].[Shifts] OFF
GO
ALTER TABLE [dbo].[OEE] ADD  DEFAULT (getdate()) FOR [TimeStamp]
GO
