Add-Type @"
using System;
using System.Runtime.InteropServices;

public class CursorMover
{
    [DllImport("user32.dll")]
    public static extern int GetSystemMetrics(int nIndex);
    
    [DllImport("user32.dll")]
    public static extern void SetCursorPos(int X, int Y);
    
    public static void MoveCursorToCenter()
    {
        int screenWidth = GetSystemMetrics(0);  // SM_CXSCREEN
        int screenHeight = GetSystemMetrics(1); // SM_CYSCREEN

        int centerX = screenWidth / 2;
        int centerY = screenHeight / 2;

        SetCursorPos(centerX, centerY);
    }
}
"@

# Перемещение курсора в центр экрана
[CursorMover]::MoveCursorToCenter()
