package OtelApi.util;

import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.common.AttributeKey;
import java.util.List;
import java.util.ArrayList;

/**
 * Utility for adding custom attributes to OpenTelemetry spans.
 * All attribute keys are prefixed with "apm.".
 *
 * <p>Supports only OpenTelemetry-compatible types:
 * boolean, Boolean, double, Double, int, Integer, long, Long, String,
 * List&lt;Boolean&gt;, List&lt;Double&gt;, List&lt;Integer&gt;, List&lt;Long&gt;, List&lt;String&gt;
 *
 * <p>This class is thread-safe and exception-safe.
 * All methods silently ignore null values and will never throw exceptions.
 *
 * @since 1.0
 */
public final class MotadataDynamicInstrumentation
{

    private static final String DEFAULT_PREFIX = "apm.";

    private MotadataDynamicInstrumentation()
    {
    }

    private static String prefixKey(String key)
    {
        try
        {
            if (key == null)
            {
                return null;
            }

            return key.startsWith(DEFAULT_PREFIX) ? key : DEFAULT_PREFIX + key;
        }
        catch (Exception exception)
        {
            return null;
        }
    }

    /**
     * Core helper method to validate key and set attribute.
     * Executes the provided setter action if key is valid.
     *
     * @param key the attribute key
     * @param value the attribute value (for null check)
     * @param setter the action to execute if validation passes
     */
    private static void safeSet(String key, Object value, Runnable setter)
    {
        try
        {
            if (key == null || value == null)
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            setter.run();

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }

    /**
     * Sets a Boolean attribute on the current span.
     * Accepts both primitive boolean and Boolean wrapper.
     *
     * @param key the attribute key
     * @param value the attribute value
     */
    public static void set(String key, Boolean value)
    {
        safeSet(key, value, () ->
        {
            String prefixed = prefixKey(key);

            Span.current().setAttribute(prefixed, value);
        });
    }

    /**
     * Sets a Double attribute on the current span.
     * Accepts both primitive double and Double wrapper.
     *
     * @param key the attribute key
     * @param value the attribute value
     */
    public static void set(String key, Double value)
    {
        safeSet(key, value, () ->
        {
            String prefixed = prefixKey(key);

            Span.current().setAttribute(prefixed, value);
        });
    }

    /**
     * Sets an Integer attribute on the current span.
     * Accepts both primitive int and Integer wrapper.
     *
     * @param key the attribute key
     * @param value the attribute value
     */
    public static void set(String key, Integer value)
    {
        safeSet(key, value, () ->
        {
            String prefixed = prefixKey(key);

            Span.current().setAttribute(prefixed, value.longValue());
        });
    }

    /**
     * Sets a Long attribute on the current span.
     * Accepts both primitive long and Long wrapper.
     *
     * @param key the attribute key
     * @param value the attribute value
     */
    public static void set(String key, Long value)
    {
        safeSet(key, value, () ->
        {
            String prefixed = prefixKey(key);

            Span.current().setAttribute(prefixed, value);
        });
    }

    /**
     * Sets a String attribute on the current span.
     *
     * @param key the attribute key
     * @param value the attribute value
     */
    public static void set(String key, String value)
    {
        safeSet(key, value, () ->
        {
            String prefixed = prefixKey(key);

            Span.current().setAttribute(prefixed, value);
        });
    }

    /**
     * Sets a List&lt;Boolean&gt; attribute on the current span.
     *
     * @param key the attribute key
     * @param value the list of boolean values
     */
    public static void setBooleanList(String key, List<Boolean> value)
    {
        try
        {
            if (key == null || value == null || value.isEmpty())
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            Span.current().setAttribute(AttributeKey.booleanArrayKey(prefixed), value);

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }

    /**
     * Sets a List&lt;Double&gt; attribute on the current span.
     *
     * @param key the attribute key
     * @param value the list of double values
     */
    public static void setDoubleList(String key, List<Double> value)
    {
        try
        {
            if (key == null || value == null || value.isEmpty())
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            Span.current().setAttribute(AttributeKey.doubleArrayKey(prefixed), value);

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }

    /**
     * Sets a List&lt;Integer&gt; attribute on the current span.
     *
     * @param key the attribute key
     * @param value the list of integer values
     */
    public static void setIntegerList(String key, List<Integer> value)
    {
        try
        {
            if (key == null || value == null || value.isEmpty())
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            // Convert Integer to Long for OpenTelemetry compatibility
            List<Long> longList = new ArrayList<>(value.size());

            for (Integer item : value)
            {
                if (item != null)
                {
                    longList.add(item.longValue());
                }
            }

            if (!longList.isEmpty())
            {
                Span.current().setAttribute(AttributeKey.longArrayKey(prefixed), longList);
            }

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }

    /**
     * Sets a List&lt;Long&gt; attribute on the current span.
     *
     * @param key the attribute key
     * @param value the list of long values
     */
    public static void setLongList(String key, List<Long> value)
    {
        try
        {
            if (key == null || value == null || value.isEmpty())
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            Span.current().setAttribute(AttributeKey.longArrayKey(prefixed), value);

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }

    /**
     * Sets a List&lt;String&gt; attribute on the current span.
     *
     * @param key the attribute key
     * @param value the list of string values
     */
    public static void setStringList(String key, List<String> value)
    {
        try
        {
            if (key == null || value == null || value.isEmpty())
            {
                return;
            }

            String prefixed = prefixKey(key);

            if (prefixed == null)
            {
                return;
            }

            Span.current().setAttribute(AttributeKey.stringArrayKey(prefixed), value);

        }
        catch (Exception exception)
        {
            // Ignore all exceptions
        }
    }
}