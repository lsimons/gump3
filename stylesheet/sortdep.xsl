<!-- ===================================================================== -->
<!-- sort a list of projects into dependency order.                        -->
<!-- ===================================================================== -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <!-- =================================================================== -->
  <!-- Output a workspace, with the projects in dependency order.          -->
  <!-- Nested projects will be promoted to siblings in the process.        -->
  <!-- =================================================================== -->

  <xsl:template match="workspace">
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:copy-of select="*[not(self::project)]"/>
      <xsl:text>&#10;</xsl:text>
      <xsl:call-template name="sort-dependencies">
        <xsl:with-param name="done" select="':'"/>
      </xsl:call-template>
    </xsl:copy>
  </xsl:template>

  <xsl:template name="sort-dependencies">
    <xsl:param name="done"/>

    <!-- ================================================================= -->
    <!-- determine a list of projects which are (1) not done and (2) only  -->
    <!-- depend on ones which have previously been processed.              -->
    <!-- ================================================================= -->

    <xsl:variable name="nextset">
      <xsl:for-each
        select=
          "//project[
            not(contains($done,concat(':',@name,':')))
              and
            count(depend)=
               count(depend[contains($done,concat(':',@project,':'))])
              and
            count(option)=
               count(option[contains($done,concat(':',@project,':'))])
           ]">
        <xsl:value-of select="concat(@name,':')"/>
      </xsl:for-each>
    </xsl:variable>

    <!-- ================================================================= -->
    <!-- if any new projects were were found, output them and recurse.     -->
    <!-- ================================================================= -->

    <xsl:if test="string-length($nextset)>0">
      <xsl:for-each
        select=
          "//project[
            contains(concat(':',$nextset),concat(':',@name,':'))
           ]">
          <xsl:text>&#10;</xsl:text>
          <xsl:copy-of select="."/>
          <xsl:text>&#10;</xsl:text>
        </xsl:for-each>
      <xsl:call-template name="sort-dependencies">
        <xsl:with-param name="done"
        select="concat($done,$nextset)"/>
      </xsl:call-template>
    </xsl:if>

    <!-- ================================================================= -->
    <!-- if no more were found, verify that all were processed.            -->
    <!-- ================================================================= -->

    <xsl:if test="string-length($nextset)=0">

      <!-- missing dependency? -->

      <xsl:for-each select="//project">
        <xsl:if test="not(contains($done,concat(':',@name,':')))">
           <xsl:variable name="project" select="@name"/>
           <xsl:for-each select="depend|option">
             <xsl:variable name="depend" select="@project"/>
             <xsl:if test="not(//project[@name=$depend])">
               <xsl:message terminate="yes">
                  <xsl:text>Dependency </xsl:text>
                  <xsl:value-of select="@project"/>
                  <xsl:text> of project </xsl:text>
                  <xsl:value-of select="$project"/>
                  <xsl:text> not found</xsl:text>
               </xsl:message>
             </xsl:if>
           </xsl:for-each>
        </xsl:if>
      </xsl:for-each>

      <!-- recursion? -->

      <xsl:for-each select="//project">
        <xsl:if test="not(contains($done,concat(':',@name,':')))">
           <xsl:message terminate="no">
              <xsl:text>Recursive dependency loop including project </xsl:text>
              <xsl:value-of select="@name"/>
           </xsl:message>
        </xsl:if>
      </xsl:for-each>

      <xsl:for-each select="//project">
        <xsl:if test="not(contains($done,concat(':',@name,':')))">
           <xsl:message terminate="yes">
              <xsl:text>Processing terminated</xsl:text>
           </xsl:message>
        </xsl:if>
      </xsl:for-each>
    </xsl:if>

  </xsl:template>

</xsl:stylesheet>
