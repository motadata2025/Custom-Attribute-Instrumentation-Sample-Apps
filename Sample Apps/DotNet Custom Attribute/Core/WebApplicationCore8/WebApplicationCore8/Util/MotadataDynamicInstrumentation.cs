using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace WebApplicationCore8.Util
{
    /// <summary>
    /// Utility for adding custom attributes (tags) to the current OpenTelemetry span in .NET.
    /// All attribute keys are automatically prefixed with "apm.".
    ///
    /// Supported types:
    /// bool, double, float, int, long, string
    /// bool[], double[], float[], int[], long[], string[]
    ///
    /// This class is thread-safe and exception-safe.
    /// All methods silently ignore null/invalid inputs and will never throw exceptions.
    /// Every operation is wrapped in try-catch for maximum robustness.
    /// </summary>
    public static class MotadataDynamicInstrumentation
    {
        private const string DefaultPrefix = "apm.";

        private static string PrefixKey(string key)
        {
            try
            {
                if (string.IsNullOrEmpty(key))
                    return null;

                return key.StartsWith(DefaultPrefix, StringComparison.Ordinal)
                    ? key
                    : DefaultPrefix + key;
            }
            catch
            {
                return null;
            }
        }

        private static Activity CurrentActivity
        {
            get
            {
                try
                {
                    return Activity.Current;
                }
                catch
                {
                    return null;
                }
            }
        }

        // ==================== Primitive types (now fully try-catch protected) ====================

        public static void Set(string key, bool value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        public static void Set(string key, double value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        public static void Set(string key, float value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        public static void Set(string key, int value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        public static void Set(string key, long value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        public static void Set(string key, string value)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || value == null || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, value);
            }
            catch
            {
                // Swallow all exceptions
            }
        }

        // ==================== Array types (already protected, kept consistent) ====================

        public static void SetBoolArray(string key, bool[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, values);
            }
            catch
            {
                // Ignore all exceptions
            }
        }

        public static void SetDoubleArray(string key, double[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, values);
            }
            catch
            {
                // Ignore all exceptions
            }
        }

        public static void SetFloatArray(string key, float[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, values);
            }
            catch
            {
                // Ignore all exceptions
            }
        }

        public static void SetIntArray(string key, int[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, values);
            }
            catch
            {
                // Ignore all exceptions
            }
        }

        public static void SetLongArray(string key, long[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                CurrentActivity.SetTag(prefixed, values);
            }
            catch
            {
                // Ignore all exceptions
            }
        }

        public static void SetStringArray(string key, string[] values)
        {
            try
            {
                if (string.IsNullOrEmpty(key) || values == null || values.Length == 0 || CurrentActivity == null)
                    return;

                string prefixed = PrefixKey(key);
                if (prefixed == null)
                    return;

                // Manual null filtering (no LINQ, maximum compatibility)
                var cleaned = new List<string>(values.Length);
                foreach (var s in values)
                {
                    if (s != null)
                        cleaned.Add(s);
                }

                if (cleaned.Count == 0)
                    return;

                CurrentActivity.SetTag(prefixed, cleaned.ToArray());
            }
            catch
            {
                // Ignore all exceptions
            }
        }
    }
}