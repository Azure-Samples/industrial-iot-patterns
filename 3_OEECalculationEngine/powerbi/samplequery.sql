SELECT l.PlantName
	  ,l.PlantLocation
	  ,a.AssetName
      ,s.ShiftName
      ,p.ProductName
      ,WorkOrder
      ,TotalUnits
      ,GoodUnits
      ,ScrapedUnits
      ,Quality
      ,PlannedDownTimeInMinutes
      ,DowntimeMinutes
      ,UptimeMinutes
      ,TotalProductionTimeInMinutes
      ,PlannedProductionTimeInMinutes
      ,Availability
      ,CycleTimeInMinutes
      ,Performance
      ,OEE
      ,AvailabilityLoss
      ,QualityLoss
      ,SpeedLoss
      ,OEEDate
  FROM OEE as oee, Locations as l, Assets as a, Products as p, Shifts as s
  WHERE oee.PlantId = l.Id and oee.AssetId = a.Id and oee.ShiftId = s.Id and oee.ProductId = p.Id
