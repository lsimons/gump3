package org.apache.gump.dynagump;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.HashMap;

import javax.imageio.ImageIO;

import org.apache.avalon.framework.configuration.Configurable;
import org.apache.avalon.framework.configuration.Configuration;
import org.apache.avalon.framework.configuration.ConfigurationException;
import org.apache.cocoon.serialization.AbstractSerializer;
import org.xml.sax.Attributes;
import org.xml.sax.SAXException;

public class ChartSerializer extends AbstractSerializer implements Configurable {
        
    protected HashMap colors;
    
    protected BufferedImage image;
    protected Graphics2D graphics;

    protected int x;
    
    protected int height;
    protected int width;
    protected String namespace;
    protected String element;
    
    protected boolean waitForChars = false;
    protected String token;

    public void configure(Configuration conf) throws ConfigurationException {
        this.height = conf.getChild("height").getValueAsInteger(10);
        this.width = conf.getChild("width").getValueAsInteger(30);
        this.namespace = conf.getChild("element").getAttribute("namespace-uri");
        this.element = conf.getChild("element").getAttribute("name");
        Configuration[] colorsConfs = conf.getChild("colors").getChildren();
        this.colors = new HashMap(colorsConfs.length);
        for (int i = 0; i < colorsConfs.length; i++) {
            Configuration color = colorsConfs[i];
            Color c = new Color(color.getAttributeAsInteger("red"),color.getAttributeAsInteger("green"),color.getAttributeAsInteger("blue"));
            colors.put(color.getAttribute("id"),c);
        }
    }
    
    /**
     * Receive notification of the beginning of a document.
     */
    public void startDocument()
    throws SAXException {
        this.x = this.width;
        this.image = new BufferedImage(width, height, BufferedImage.TYPE_4BYTE_ABGR);
        this.graphics = (Graphics2D) image.getGraphics();
    }

    /**
     * Receive notification of the end of a document.
     */
    public void endDocument()
    throws SAXException {
        try {
            ImageIO.write(image, "png", output);
        } catch (IOException e) {
            throw new RuntimeException("An error occurred while serializing the image", e);
        }
    }

    /**
     * Receive notification of the beginning of an element.
     *
     * @param uri The Namespace URI, or the empty string if the element has no
     *            Namespace URI or if Namespace
     *            processing is not being performed.
     * @param loc The local name (without prefix), or the empty string if
     *            Namespace processing is not being performed.
     * @param raw The raw XML 1.0 name (with prefix), or the empty string if
     *            raw names are not available.
     * @param a The attributes attached to the element. If there are no
     *          attributes, it shall be an empty Attributes object.
     */
    public void startElement(String uri, String loc, String raw, Attributes a)
    throws SAXException {
        this.waitForChars = (this.namespace.equals(uri) && this.element.equals(loc));
        this.token = "";
    }

    /**
     * Receive notification of the end of an element.
     *
     * @param uri The Namespace URI, or the empty string if the element has no
     *            Namespace URI or if Namespace
     *            processing is not being performed.
     * @param loc The local name (without prefix), or the empty string if
     *            Namespace processing is not being performed.
     * @param raw The raw XML 1.0 name (with prefix), or the empty string if
     *            raw names are not available.
     */
    public void endElement(String uri, String loc, String raw)
    throws SAXException {
        if ((this.waitForChars) && (x > 0)) {
            x--;
            Color color = (Color) this.colors.get(this.token);
            if (color == null) color = Color.WHITE;
            this.graphics.setColor(color);
            this.graphics.drawLine(x,0,x,height);
            this.waitForChars = false;
        }
    }

    /**
     * Receive notification of character data.
     *
     * @param c The characters from the XML document.
     * @param start The start position in the array.
     * @param len The number of characters to read from the array.
     */
    public void characters(char c[], int start, int len)
    throws SAXException {
        if (this.waitForChars) this.token += new String(c);
    }
    
    public String getMimeType() {
        return "image/png";
    }
}

